from __future__ import annotations

import json
import time
from typing import Sequence

import pandas as pd
import streamlit as st

from send_sms import (
    DEFAULT_ADD_DELAY_SECONDS,
    DEFAULT_FIND_DELAY_SECONDS,
    DEFAULT_SEND_TIMEOUT,
    GATE_PHONE_COLUMN_INDEX,
    SUPPLEMENT_PHONE_COLUMN_INDEX,
    SUPPLEMENT_SHEET_NAME,
    AppConfig,
    ConfigurationError,
    GateConfig,
    SheetAnalysis,
    SmsGatewayClient,
    SmsResult,
    SpreadsheetError,
    analyze_phone_numbers,
    analyze_sheet,
    build_add_messages,
    build_find_messages,
    load_config,
    normalize_phone_number,
    save_sheet_numbers,
)


st.set_page_config(
    page_title="Sprava GSM zavor",
    layout="wide",
)


def inject_styles() -> None:
    st.markdown(
        """
        <style>
        .stApp {
            background:
                radial-gradient(circle at top right, rgba(255, 210, 168, 0.26), transparent 34%),
                radial-gradient(circle at bottom left, rgba(76, 116, 91, 0.16), transparent 28%),
                linear-gradient(180deg, #f4ecdf 0%, #fbf6ed 48%, #eef2e8 100%);
        }
        .main .block-container {
            max-width: 1320px;
            padding-top: 2.4rem;
            padding-bottom: 2rem;
        }
        html, body, [class*="css"]  {
            font-family: "Trebuchet MS", "Segoe UI", sans-serif;
            color: #1f2d24;
        }
        h1, h2, h3 {
            font-family: Georgia, "Palatino Linotype", serif;
            letter-spacing: 0.02em;
            color: #163f32;
        }
        [data-testid="stSidebar"] {
            background: linear-gradient(180deg, #173d33 0%, #1e5042 58%, #275e4d 100%);
        }
        [data-testid="stSidebar"] * {
            color: #f6f0e5;
        }
        [data-testid="stMetric"] {
            background: rgba(255, 255, 255, 0.72);
            border: 1px solid rgba(52, 76, 64, 0.14);
            border-radius: 20px;
            padding: 0.9rem 1rem;
            box-shadow: 0 18px 36px rgba(45, 52, 46, 0.08);
        }
        .hero-panel {
            background: linear-gradient(135deg, rgba(255, 248, 235, 0.96), rgba(255, 236, 210, 0.92));
            border: 1px solid rgba(73, 56, 37, 0.12);
            border-radius: 26px;
            padding: 1.5rem 1.7rem;
            box-shadow: 0 24px 55px rgba(64, 53, 38, 0.12);
            margin-bottom: 1rem;
        }
        .hero-title {
            font-size: 2.2rem;
            line-height: 1.1;
            margin-bottom: 0.35rem;
            color: #153c30;
        }
        .hero-text {
            color: #3c4d43;
            max-width: 56rem;
        }
        .hero-grid {
            display: grid;
            grid-template-columns: repeat(3, minmax(0, 1fr));
            gap: 0.85rem;
            margin-top: 1rem;
        }
        .info-card {
            background: rgba(255, 255, 255, 0.62);
            border: 1px solid rgba(77, 63, 49, 0.12);
            border-radius: 18px;
            padding: 0.9rem 1rem;
        }
        .info-label {
            font-size: 0.78rem;
            text-transform: uppercase;
            letter-spacing: 0.08em;
            color: #6f6a5f;
            margin-bottom: 0.2rem;
        }
        .info-value {
            font-size: 1rem;
            color: #173c31;
            font-weight: 600;
        }
        .notice-panel {
            background: rgba(207, 116, 40, 0.1);
            border-left: 5px solid #b95f22;
            border-radius: 14px;
            padding: 0.9rem 1rem;
            margin: 0.9rem 0 1rem 0;
            color: #5a4029;
        }
        .stButton > button, .stDownloadButton > button {
            border-radius: 999px;
            border: none;
            background: linear-gradient(135deg, #1c5b48 0%, #2b7159 100%);
            color: white;
            font-weight: 700;
            padding: 0.55rem 1.15rem;
            box-shadow: 0 10px 22px rgba(28, 91, 72, 0.22);
        }
        .stButton > button:hover, .stDownloadButton > button:hover {
            background: linear-gradient(135deg, #164837 0%, #225843 100%);
            color: white;
        }
        [data-baseweb="tab-list"] {
            gap: 0.5rem;
        }
        button[role="tab"] {
            border-radius: 999px;
            background: rgba(255, 255, 255, 0.55);
            border: 1px solid rgba(39, 66, 55, 0.08);
        }
        button[role="tab"][aria-selected="true"] {
            background: #173f32;
            color: #ffffff;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


@st.cache_data(show_spinner=False)
def load_config_cached(config_path: str) -> AppConfig:
    return load_config(config_path)


@st.cache_data(show_spinner=False)
def load_analysis_cached(config_path: str, sheet_name: str, column_index: int) -> SheetAnalysis:
    config = load_config(config_path)
    return analyze_sheet(config, sheet_name, column_index=column_index)


def gate_label(gate: GateConfig) -> str:
    return f"{gate.id}: {gate.sheet}"


def rows_dataframe(analysis: SheetAnalysis, *, statuses: Sequence[str] | None = None) -> pd.DataFrame:
    rows = analysis.rows
    if statuses is not None:
        rows = [row for row in rows if row.status in statuses]

    return pd.DataFrame(
        [
            {
                "radek": row.row_number,
                "puvodni_hodnota": row.raw_value,
                "normalizovane_cislo": row.normalized or "",
                "stav": row.status,
                "chyba": row.error or "",
            }
            for row in rows
        ]
    )


def editable_numbers_dataframe(analysis: SheetAnalysis) -> pd.DataFrame:
    values = [
        row.normalized or row.raw_value
        for row in analysis.rows
        if row.status != "blank"
    ]
    return pd.DataFrame({"telefon": values})


def messages_dataframe(messages: Sequence[str]) -> pd.DataFrame:
    return pd.DataFrame(
        [{"poradi": index, "prikaz_sms": message} for index, message in enumerate(messages, start=1)]
    )


def results_dataframe(results: Sequence[SmsResult]) -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "ok": result.ok,
                "telefon": result.phone,
                "zprava": result.message,
                "status_code": result.status_code or "",
                "chyba": result.error or "",
                "odpoved": json.dumps(result.payload, ensure_ascii=False)
                if result.payload is not None
                else "",
            }
            for result in results
        ]
    )


def render_hero(config: AppConfig, gate: GateConfig) -> None:
    st.markdown(
        f"""
        <div class="hero-panel">
            <div class="hero-title">Sprava GSM zavor</div>
            <div class="hero-text">
                Rozhrani pro kontrolu telefonnich cisel v Excel seznamech a bezpecne spousteni prikazu
                <strong>ADD</strong> a <strong>FIND</strong> pres SMS gateway. Aplikace pocita s limitem modulu:
                ADD pracuje po davkach, FIND jde po jednom cisle.
            </div>
            <div class="hero-grid">
                <div class="info-card">
                    <div class="info-label">Aktivni brana</div>
                    <div class="info-value">{gate.id} / {gate.sheet}</div>
                </div>
                <div class="info-card">
                    <div class="info-label">Cislo brany</div>
                    <div class="info-value">{gate.phone}</div>
                </div>
                <div class="info-card">
                    <div class="info-label">Gateway endpoint</div>
                    <div class="info-value">{config.send_endpoint}</div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_result_summary(results: Sequence[SmsResult]) -> None:
    success_count = sum(1 for result in results if result.ok)
    failure_count = len(results) - success_count
    cols = st.columns(4)
    cols[0].metric("Zpracovano", len(results))
    cols[1].metric("Uspech", success_count)
    cols[2].metric("Chyba", failure_count)
    cols[3].metric("Posledni status", "OK" if not results or results[-1].ok else "CHYBA")

    if results:
        st.dataframe(results_dataframe(results), use_container_width=True, height=320)


def run_messages_ui(
    *,
    config: AppConfig,
    recipient_phone: str,
    messages: Sequence[str],
    dry_run: bool,
    pause_seconds: float,
    stop_on_error: bool,
    timeout: float,
    operation_label: str,
) -> list[SmsResult]:
    client = SmsGatewayClient(config)
    progress = st.progress(0.0, text=f"{operation_label}: pripravuji")
    status_placeholder = st.empty()
    results: list[SmsResult] = []

    for index, message in enumerate(messages, start=1):
        status_placeholder.info(f"{operation_label}: zprava {index} z {len(messages)}")
        if dry_run:
            result = SmsResult(
                ok=True,
                phone=recipient_phone,
                message=message,
                payload={"dry_run": True},
            )
        else:
            result = client.send_sms(recipient_phone, message, timeout=timeout)

        results.append(result)
        progress.progress(index / len(messages), text=f"{operation_label}: {index}/{len(messages)}")

        if stop_on_error and not result.ok:
            status_placeholder.error("Odesilani zastaveno po prvni chybe.")
            break

        if not dry_run and pause_seconds > 0 and index < len(messages):
            status_placeholder.info(f"Cekam {pause_seconds:.0f} s pred dalsi SMS.")
            time.sleep(pause_seconds)

    if results and all(result.ok for result in results):
        status_placeholder.success(f"{operation_label}: dokonceno bez chyby.")
    elif results:
        status_placeholder.warning(f"{operation_label}: dokonceno s chybou.")

    return results


def render_sheet_health(analysis: SheetAnalysis, *, download_prefix: str) -> None:
    metric_cols = st.columns(4)
    metric_cols[0].metric("Unikatni cisla", analysis.unique_row_count)
    metric_cols[1].metric("Vsechna validni", analysis.valid_row_count)
    metric_cols[2].metric("Duplicity", len(analysis.duplicate_numbers))
    metric_cols[3].metric("Chybne radky", analysis.invalid_row_count)

    valid_df = rows_dataframe(analysis, statuses=("valid", "duplicate"))
    st.dataframe(valid_df, use_container_width=True, height=280)
    st.download_button(
        "Stahnout normalizovany seznam CSV",
        data=valid_df.to_csv(index=False).encode("utf-8-sig"),
        file_name=f"{download_prefix}_normalized.csv",
        mime="text/csv",
    )

    if analysis.duplicate_numbers:
        duplicates_df = pd.DataFrame(
            [{"telefon": phone_number} for phone_number in analysis.duplicate_numbers]
        )
        st.caption("Duplicity v normalizovanem seznamu")
        st.dataframe(duplicates_df, use_container_width=True, height=180)

    if analysis.invalid_rows:
        st.warning("Ve sheetu jsou chybne hodnoty. Odesilani bude blokovano, dokud je neopravite.")
        invalid_df = rows_dataframe(analysis, statuses=("invalid",))
        st.dataframe(invalid_df, use_container_width=True, height=220)


def render_flash_message() -> None:
    flash_kind = st.session_state.pop("flash_kind", None)
    flash_message = st.session_state.pop("flash_message", None)
    if flash_kind and flash_message:
        getattr(st, flash_kind)(flash_message)


def render_sheet_editor(
    *,
    config: AppConfig,
    title: str,
    sheet_name: str,
    column_index: int,
    analysis: SheetAnalysis | None,
    error_message: str | None,
    editor_key: str,
    save_button_key: str,
    backup_key: str,
) -> None:
    st.subheader(title)
    st.caption(
        "Editor uklada jen cilovy sloupec se seznamem telefonu. Cisla se pri ulozeni normalizuji,"
        " prazdne radky se ignoruji a duplicity se odstrani podle prvniho vyskytu."
    )

    if error_message:
        st.error(error_message)
        return

    if analysis is None:
        st.info("Sheet neni k dispozici.")
        return

    draft_df = st.data_editor(
        editable_numbers_dataframe(analysis),
        num_rows="dynamic",
        hide_index=True,
        use_container_width=True,
        height=420,
        key=editor_key,
        column_config={
            "telefon": st.column_config.TextColumn(
                "Telefon",
                help="Zadej lokalni cislo nebo tvar s +420. Pri ulozeni se seznam sjednoti.",
                width="large",
            )
        },
    )

    editor_values = draft_df.get("telefon", pd.Series(dtype="object")).tolist()
    draft_analysis = analyze_phone_numbers(editor_values, source_name=f"editor:{sheet_name}")

    metrics = st.columns(4)
    metrics[0].metric("Radku v editoru", len(editor_values))
    metrics[1].metric("Po ulozeni zustane", draft_analysis.unique_row_count)
    metrics[2].metric("Duplicity", len(draft_analysis.duplicate_numbers))
    metrics[3].metric("Nevalidni", draft_analysis.invalid_row_count)

    if draft_analysis.duplicate_numbers:
        duplicates_df = pd.DataFrame(
            [{"telefon": phone_number} for phone_number in draft_analysis.duplicate_numbers]
        )
        st.info("Duplicity jsou povolene v editoru, ale pri ulozeni budou odstraneny.")
        st.dataframe(duplicates_df, use_container_width=True, height=180)

    if draft_analysis.invalid_rows:
        st.warning("Nevalidni radky blokují ulozeni do Excelu.")
        st.dataframe(
            rows_dataframe(draft_analysis, statuses=("invalid",)),
            use_container_width=True,
            height=220,
        )

    create_backup = st.checkbox("Vytvorit zalohu XLSX pred ulozenim", value=False, key=backup_key)
    save_disabled = draft_analysis.invalid_row_count > 0
    if st.button("Ulozit zmeny do Excelu", key=save_button_key, use_container_width=True, disabled=save_disabled):
        try:
            save_result = save_sheet_numbers(
                config,
                sheet_name,
                column_index=column_index,
                values=editor_values,
                create_backup=create_backup,
            )
        except SpreadsheetError as exc:
            st.error(str(exc))
        else:
            if save_result.backup_path:
                st.session_state["flash_message"] = (
                    f"Sheet '{sheet_name}' ulozen. Zapsano {save_result.rows_written} cisel. "
                    f"Zaloha: {save_result.backup_path}"
                )
            else:
                st.session_state["flash_message"] = (
                    f"Sheet '{sheet_name}' ulozen. Zapsano {save_result.rows_written} cisel."
                )
            st.session_state["flash_kind"] = "success"
            st.cache_data.clear()
            st.rerun()


def main() -> None:
    inject_styles()
    st.session_state.setdefault("config_path", "config.toml")

    with st.sidebar:
        st.title("Nastaveni")
        config_path = st.text_input(
            "Konfiguracni soubor",
            value=st.session_state["config_path"],
            help="Cesta k TOML souboru s gateway a seznamem bran.",
        )
        st.session_state["config_path"] = config_path

        if st.button("Obnovit konfiguraci a data", use_container_width=True):
            st.cache_data.clear()
            st.rerun()

        st.markdown(
            """
            <div class="notice-panel">
                Nejdriv opravte chybne radky v Excelu, pak spoustejte ostrou synchronizaci.
                Bezpecnejsi vychozi rezim je <strong>dry-run</strong>.
            </div>
            """,
            unsafe_allow_html=True,
        )

        try:
            config = load_config_cached(config_path)
        except ConfigurationError as exc:
            st.error(str(exc))
            st.info("Vytvorte localni config.toml podle config.example.toml.")
            st.stop()

        gate_options = sorted(config.gates.values(), key=lambda gate: gate.id)
        selected_gate = st.selectbox(
            "Vyber branu",
            options=gate_options,
            format_func=gate_label,
            index=0,
        )

        st.caption(f"Excel: {config.excel_path}")
        st.caption(f"Gateway: {config.gateway_base}")

    render_flash_message()
    render_hero(config, selected_gate)

    try:
        gate_analysis = load_analysis_cached(
            config_path,
            selected_gate.sheet,
            GATE_PHONE_COLUMN_INDEX,
        )
        gate_error = None
    except SpreadsheetError as exc:
        gate_analysis = None
        gate_error = str(exc)

    try:
        supplement_analysis = load_analysis_cached(
            config_path,
            SUPPLEMENT_SHEET_NAME,
            SUPPLEMENT_PHONE_COLUMN_INDEX,
        )
        supplement_error = None
    except SpreadsheetError as exc:
        supplement_analysis = None
        supplement_error = str(exc)

    overview_tab, editor_tab, add_tab, supplement_tab, find_tab, direct_tab, control_tab = st.tabs(
        [
            "Prehled",
            "Editor sheetu",
            "ADD ze sheetu",
            "Doplneni",
            "FIND",
            "Jednorazova SMS",
            "Kontrola dat",
        ]
    )

    with overview_tab:
        cols = st.columns(4)
        cols[0].metric("Sheet brany", selected_gate.sheet)
        cols[1].metric("Unikatni cisla", gate_analysis.unique_row_count if gate_analysis else "N/A")
        cols[2].metric("Duplicity", len(gate_analysis.duplicate_numbers) if gate_analysis else "N/A")
        cols[3].metric("Doplnit", supplement_analysis.unique_row_count if supplement_analysis else "N/A")

        if gate_error:
            st.error(gate_error)
        elif gate_analysis:
            preview_messages = build_add_messages(selected_gate.password, gate_analysis.unique_numbers[:20], batch_size=10)
            st.subheader("Rychly nahled pripravenych ADD prikazu")
            st.dataframe(messages_dataframe(preview_messages), use_container_width=True, height=220)
            st.subheader("Prvnich 25 radku aktivniho sheetu")
            st.dataframe(rows_dataframe(gate_analysis).head(25), use_container_width=True, height=320)

        if supplement_error:
            st.info(f"Sheet '{SUPPLEMENT_SHEET_NAME}' neni pripraven: {supplement_error}")

    with editor_tab:
        gate_editor_tab, supplement_editor_tab = st.tabs(
            [
                f"Sheet brany {selected_gate.id}",
                SUPPLEMENT_SHEET_NAME,
            ]
        )

        with gate_editor_tab:
            render_sheet_editor(
                config=config,
                title=f"Editor seznamu pro {selected_gate.sheet}",
                sheet_name=selected_gate.sheet,
                column_index=GATE_PHONE_COLUMN_INDEX,
                analysis=gate_analysis,
                error_message=gate_error,
                editor_key=f"editor_gate_{selected_gate.id}",
                save_button_key=f"save_gate_{selected_gate.id}",
                backup_key=f"backup_gate_{selected_gate.id}",
            )

        with supplement_editor_tab:
            render_sheet_editor(
                config=config,
                title=f"Editor seznamu pro {SUPPLEMENT_SHEET_NAME}",
                sheet_name=SUPPLEMENT_SHEET_NAME,
                column_index=SUPPLEMENT_PHONE_COLUMN_INDEX,
                analysis=supplement_analysis,
                error_message=supplement_error,
                editor_key="editor_supplement",
                save_button_key="save_supplement",
                backup_key="backup_supplement",
            )

    with add_tab:
        st.subheader("Davkove pridani cisel z aktivniho sheetu")
        if gate_error:
            st.error(gate_error)
        elif gate_analysis is None:
            st.info("Sheet se nepodarilo nacist.")
        else:
            with st.form("add_batch_form"):
                col1, col2, col3 = st.columns(3)
                batch_size = int(col1.number_input("Cisel v jedne SMS", min_value=1, max_value=10, value=10, step=1))
                pause_seconds = float(
                    col2.number_input("Pauza mezi SMS [s]", min_value=0.0, value=DEFAULT_ADD_DELAY_SECONDS, step=5.0)
                )
                timeout = float(
                    col3.number_input("HTTP timeout [s]", min_value=1.0, value=DEFAULT_SEND_TIMEOUT, step=1.0)
                )
                dry_run = st.checkbox("Dry-run bez odeslani", value=True)
                continue_on_error = st.checkbox("Pokracovat i po chybe", value=False)

                prepared_messages = build_add_messages(
                    selected_gate.password,
                    gate_analysis.unique_numbers,
                    batch_size=batch_size,
                )
                st.caption(
                    f"Pripraveno {len(prepared_messages)} SMS pro {gate_analysis.unique_row_count} unikatnich cisel."
                )
                st.dataframe(messages_dataframe(prepared_messages[:12]), use_container_width=True, height=260)
                submitted_add = st.form_submit_button("Spustit ADD synchronizaci")

            if submitted_add:
                if gate_analysis.invalid_rows:
                    st.error("Ve sheetu jsou chybna cisla. Opravte je pred synchronizaci.")
                elif not prepared_messages:
                    st.warning("Neni co odeslat.")
                else:
                    results = run_messages_ui(
                        config=config,
                        recipient_phone=selected_gate.phone,
                        messages=prepared_messages,
                        dry_run=dry_run,
                        pause_seconds=pause_seconds,
                        stop_on_error=not continue_on_error,
                        timeout=timeout,
                        operation_label="ADD synchronizace",
                    )
                    render_result_summary(results)

    with supplement_tab:
        st.subheader("Doplneni ze sheetu Doplnit")
        if supplement_error:
            st.info(supplement_error)
        elif supplement_analysis is None:
            st.info("Sheet Doplnit se nepodarilo nacist.")
        else:
            with st.form("supplement_form"):
                col1, col2, col3 = st.columns(3)
                batch_size = int(col1.number_input("Cisel v jedne SMS", min_value=1, max_value=10, value=10, step=1))
                pause_seconds = float(
                    col2.number_input("Pauza mezi SMS [s]", min_value=0.0, value=DEFAULT_ADD_DELAY_SECONDS, step=5.0)
                )
                timeout = float(
                    col3.number_input("HTTP timeout [s]", min_value=1.0, value=DEFAULT_SEND_TIMEOUT, step=1.0)
                )
                dry_run = st.checkbox("Dry-run bez odeslani", value=True, key="supplement_dry_run")
                continue_on_error = st.checkbox("Pokracovat i po chybe", value=False, key="supplement_continue")

                prepared_messages = build_add_messages(
                    selected_gate.password,
                    supplement_analysis.unique_numbers,
                    batch_size=batch_size,
                )
                st.caption(
                    f"Pripraveno {len(prepared_messages)} SMS pro {supplement_analysis.unique_row_count} unikatnich cisel."
                )
                st.dataframe(messages_dataframe(prepared_messages[:12]), use_container_width=True, height=260)
                submitted_supplement = st.form_submit_button("Spustit doplneni")

            if submitted_supplement:
                if supplement_analysis.invalid_rows:
                    st.error("Sheet Doplnit obsahuje chybna cisla.")
                elif not prepared_messages:
                    st.warning("Neni co odeslat.")
                else:
                    results = run_messages_ui(
                        config=config,
                        recipient_phone=selected_gate.phone,
                        messages=prepared_messages,
                        dry_run=dry_run,
                        pause_seconds=pause_seconds,
                        stop_on_error=not continue_on_error,
                        timeout=timeout,
                        operation_label="Doplneni",
                    )
                    render_result_summary(results)

    with find_tab:
        left_col, right_col = st.columns(2)

        with left_col:
            st.subheader("FIND jednoho cisla")
            with st.form("find_one_form"):
                searched_number = st.text_input("Hledane cislo", placeholder="777530100 nebo +420777530100")
                timeout = float(
                    st.number_input("HTTP timeout [s]", min_value=1.0, value=DEFAULT_SEND_TIMEOUT, step=1.0)
                )
                dry_run = st.checkbox("Dry-run bez odeslani", value=True, key="find_one_dry_run")
                submitted_find_one = st.form_submit_button("Odeslat FIND")

            if submitted_find_one:
                try:
                    normalized_number = normalize_phone_number(searched_number)
                except ValueError as exc:
                    st.error(str(exc))
                else:
                    message = f"{selected_gate.password} FIND {normalized_number}"
                    results = run_messages_ui(
                        config=config,
                        recipient_phone=selected_gate.phone,
                        messages=[message],
                        dry_run=dry_run,
                        pause_seconds=0.0,
                        stop_on_error=True,
                        timeout=timeout,
                        operation_label="FIND jednoho cisla",
                    )
                    render_result_summary(results)

        with right_col:
            st.subheader("FIND celeho sheetu")
            if gate_error:
                st.error(gate_error)
            elif gate_analysis is not None:
                with st.form("find_sheet_form"):
                    pause_seconds = float(
                        st.number_input(
                            "Pauza mezi SMS [s]",
                            min_value=0.0,
                            value=DEFAULT_FIND_DELAY_SECONDS,
                            step=5.0,
                            key="find_pause",
                        )
                    )
                    timeout = float(
                        st.number_input(
                            "HTTP timeout [s]",
                            min_value=1.0,
                            value=DEFAULT_SEND_TIMEOUT,
                            step=1.0,
                            key="find_timeout",
                        )
                    )
                    dry_run = st.checkbox("Dry-run bez odeslani", value=True, key="find_sheet_dry_run")
                    continue_on_error = st.checkbox("Pokracovat i po chybe", value=False, key="find_continue")
                    prepared_messages = build_find_messages(selected_gate.password, gate_analysis.unique_numbers)
                    st.caption(f"Pripraveno {len(prepared_messages)} FIND prikazu.")
                    st.dataframe(messages_dataframe(prepared_messages[:20]), use_container_width=True, height=260)
                    submitted_find_sheet = st.form_submit_button("Spustit FIND pro sheet")

                if submitted_find_sheet:
                    if gate_analysis.invalid_rows:
                        st.error("Ve sheetu jsou chybna cisla. Opravte je pred FIND operaci.")
                    elif not prepared_messages:
                        st.warning("Neni co odeslat.")
                    else:
                        results = run_messages_ui(
                            config=config,
                            recipient_phone=selected_gate.phone,
                            messages=prepared_messages,
                            dry_run=dry_run,
                            pause_seconds=pause_seconds,
                            stop_on_error=not continue_on_error,
                            timeout=timeout,
                            operation_label="FIND cely sheet",
                        )
                        render_result_summary(results)

    with direct_tab:
        st.subheader("Jednorazove odeslani SMS pres gateway")
        with st.form("direct_sms_form"):
            recipient_phone = st.text_input("Cilove cislo", placeholder="+420602191729")
            message = st.text_area("Text zpravy", height=140)
            timeout = float(
                st.number_input(
                    "HTTP timeout [s]",
                    min_value=1.0,
                    value=DEFAULT_SEND_TIMEOUT,
                    step=1.0,
                    key="direct_timeout",
                )
            )
            dry_run = st.checkbox("Dry-run bez odeslani", value=True, key="direct_dry_run")
            submitted_direct = st.form_submit_button("Odeslat SMS")

        if submitted_direct:
            try:
                normalized_phone = normalize_phone_number(recipient_phone)
            except ValueError as exc:
                st.error(str(exc))
            else:
                cleaned_message = message.strip()
                if not cleaned_message:
                    st.error("Text zpravy nesmi byt prazdny.")
                else:
                    results = run_messages_ui(
                        config=config,
                        recipient_phone=normalized_phone,
                        messages=[cleaned_message],
                        dry_run=dry_run,
                        pause_seconds=0.0,
                        stop_on_error=True,
                        timeout=timeout,
                        operation_label="Jednorazova SMS",
                    )
                    render_result_summary(results)

    with control_tab:
        st.subheader("Kvalita vstupnich dat")
        if gate_error:
            st.error(gate_error)
        elif gate_analysis:
            st.markdown(f"### Aktivni sheet: {selected_gate.sheet}")
            render_sheet_health(
                gate_analysis,
                download_prefix=f"gate_{selected_gate.id}",
            )

        if supplement_error:
            st.info(f"Sheet '{SUPPLEMENT_SHEET_NAME}' neni dostupny: {supplement_error}")
        elif supplement_analysis:
            st.markdown(f"### Sheet: {SUPPLEMENT_SHEET_NAME}")
            render_sheet_health(
                supplement_analysis,
                download_prefix="supplement",
            )


if __name__ == "__main__":
    main()

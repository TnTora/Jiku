import { createContext } from "svelte";

export interface JikuError {
    short: string,
    details?: any,
}

export const [getJikuErrorsContext, setJikuErrorsContext] = createContext<JikuError[]>();


export interface ConfirmationPopupContext {
    show_input_modal: boolean,
    use_modal_input: boolean,
    input_description: string,
    text_input_value: string | null,
    text_input_default: string,
    modalOk: () => any,
    modalCancel: () => any,
}

export const [getConfirmationPopupContext, setConfirmationPopupContext] = createContext<ConfirmationPopupContext>();
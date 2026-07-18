import { browser } from "$app/env";
import { createContext, getContext, setContext } from "svelte";

export interface JikuError {
    short: string,
    details?: any,
}

export class JikuErrorsContext {
    errors: JikuError[];
    interval: ReturnType<typeof setInterval> | null;
    binded_callback: () => void;

    constructor(errors: JikuError[] = []) {
        this.errors = $state(errors);
        this.interval = null;
        this.binded_callback = this.mousemoveCallback.bind(this)
    }

    addInterval() {
        this.interval = setInterval(() => {
            this.errors.length = 0;
            this.interval = null;
        }, 5000);
    }

    mousemoveCallback() {
        document.removeEventListener("mousemove", this.binded_callback);
        this.addInterval();
    }

    push(error: JikuError) {
        this.errors.push(error);
        if (this.interval) {
            clearInterval(this.interval);
            this.addInterval();
        } else {
            document.addEventListener("mousemove", this.binded_callback);
        }
    }
}


const ERRORS_CONTEXT_KEY = Symbol("ERRORS");

export function setJikuErrorsContext(errors: JikuError[] = []) {
    return setContext(ERRORS_CONTEXT_KEY, new JikuErrorsContext(errors));
}

export function getJikuErrorsContext() {
    return getContext<ReturnType<typeof setJikuErrorsContext>>(ERRORS_CONTEXT_KEY);
}

// export const [getJikuErrorsContext, setJikuErrorsContext] = createContext<JikuError[]>();


export interface ConfirmationPopupContext {
    show: boolean,
    text: string,
    onOk: () => any,
    onCancel: () => any,
}

export const [getConfirmationPopupContext, setConfirmationPopupContext] = createContext<ConfirmationPopupContext>();

export interface TextInputPopupContext {
    show: boolean,
    text: string,
    text_input_value: string | null,
    text_input_default: string,
    onOk: () => any,
    onCancel: () => any,
}

export const [getTextInputPopupContext, setTextInputPopupContext] = createContext<TextInputPopupContext>();
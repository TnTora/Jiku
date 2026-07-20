import { browser } from "$app/env";
import { createContext, getContext, setContext } from "svelte";

export interface JikuError {
    short: string,
    details?: any,
}

export class JikuErrorsContext {
    errors: JikuError[];
    show_all: boolean;
    timeout: ReturnType<typeof setTimeout> | null;
    binded_callback: () => void;

    constructor(errors: JikuError[] = []) {
        this.errors = $state(errors);
        this.show_all = $state(false);
        this.timeout = null;
        this.binded_callback = this.mousemoveCallback.bind(this)
    }

    addTimeout() {
        this.timeout = setTimeout(() => {
            this.errors.length = 0;
            this.timeout = null;
            this.show_all = false;
            console.log("cleared errors");
        }, 5000);
    }

    clearTimeout() {
        if (this.timeout === null) { return; }

        clearTimeout(this.timeout);
        this.timeout = null;
    }

    mousemoveCallback() {
        document.removeEventListener("mousemove", this.binded_callback);
        this.addTimeout();
    }

    push(error: JikuError) {
        this.errors.push(error);

        if (this.show_all) { return; }

        if (this.timeout) {
            clearTimeout(this.timeout);
            this.addTimeout();
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
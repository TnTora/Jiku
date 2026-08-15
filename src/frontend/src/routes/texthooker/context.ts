import { createContext } from "svelte";

export interface TextHookerOptions {
    font?: string,
    font_size: number,
    line_height: number,
    max_repetition: number,
    vertical: boolean,
    websocket_url?: string,
}

export const [getTextHookerOptionsContext, setTextHookerOptionsContext] = createContext<TextHookerOptions>();

export const default_texthooker_options: TextHookerOptions = {
    font: undefined,
    font_size: 22,
    line_height: 1.75,
    max_repetition: 0,
    vertical: false,
    websocket_url: "ws://localhost:6677",
}
import { createContext } from "svelte";

interface TextHookerOptions {
    websocket_url?: string,
    font?: string,
    font_size: number,
    line_height: number,
    vertical: boolean,
}

export const [getTextHookerOptionsContext, setTextHookerOptionsContext] = createContext<TextHookerOptions>();
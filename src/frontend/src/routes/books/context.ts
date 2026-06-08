import { createContext } from "svelte";

export interface SelectCollectionPopupContext {
    show: boolean,
    selected_id: number | null,
    onOk: (collection_id:number) => any,
}

export const [getSelectCollectionPopupContext, setSelectColelctionPopupContext] = createContext<SelectCollectionPopupContext>();
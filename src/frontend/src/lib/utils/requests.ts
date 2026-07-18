import type { JikuError, JikuErrorsContext } from "$lib/utils/context.svelte";

interface ErrorParams {
    err_msg: string,
    err_context?: JikuErrorsContext,
}


export async function api_fetch(
    url: string,
    fetch_params: RequestInit = {},
    err_params: ErrorParams = { err_msg: "" },
) {
    if (url[0] == "/") {
        url = url.slice(1);
    }

    try {
        let res = await fetch(`/api_bridge/${url}`, fetch_params);
        // console.log(res);
        if (!res.ok) {
            // console.error(`Error: ${err_params.err_msg}`);
            // if (err_params.err_context) {
            //     err_params.err_context.push({
            //         short: err_params.err_msg,
            //     });
            // }
            throw new Error(`api_fetch failed`);
        }
        return res;
    } catch (error) {
        console.error(`Error: ${err_params.err_msg}`, error);
        if (err_params.err_context) {
            err_params.err_context.push({
                short: err_params.err_msg
            });
        }
        throw error;
    }
}


export async function addBookToCollection(
    {book_id, collection_id, errors}:
    {book_id: number, collection_id: number, errors: JikuErrorsContext}
) {
    api_fetch("books/add_book_to_collection", {
        method: "POST",
        headers: {
            "accept": "application/json",
            "Content-Type": "application/json",
        },
        body: JSON.stringify({
            book_id: book_id,
            collection_id: collection_id
        }),
    }, {
        err_msg: "Failed to add book to collection",
        err_context: errors
    });
}


export async function removeBookFromCollection(
    {book_id, collection_id, errors}:
    {book_id: number, collection_id: number, errors: JikuErrorsContext}
) {
    await api_fetch("books/remove_from_collection", {
        method: "DELETE",
        headers: {
            "accept": "application/json",
            "Content-Type": "application/json",
        },
        body: JSON.stringify({
            book_id: book_id,
            collection_id: collection_id
        }),
    }, {
        err_msg: "Failed to remove book from collection",
        err_context: errors
    });
}

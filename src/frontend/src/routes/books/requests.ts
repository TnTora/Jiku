import type { JikuError } from "$lib/utils/context";


export function addBookToCollection(book_id: number, errors: Array<JikuError>) {
    return async (collection_id:number) => {
        try {
            let res = await fetch("/api_bridge/books/add_book_to_collection/", {
                method: "POST",
                headers: {
                    "accept": "application/json",
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({
                    book_id: book_id,
                    collection_id: collection_id
                })
            });
        } catch (error) {
            console.error("Failed to add book to collection", error);
            errors.push({
                short: "Failed to add book to collection",
                details: error,
            });
            throw error;
        }
    }
}
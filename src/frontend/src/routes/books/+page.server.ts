export const load = async ({ url, fetch }) => {
    let res = await fetch(`/api_bridge/books/books_info?${url.searchParams.toString()}`);
    let books = await res.json();
    res = await fetch(`/api_bridge/books/collections`);
	let collections = await res.json();
    res = await fetch(`/api_bridge/books/creators`);
	let creators = await res.json();
    console.log(books, collections, creators);
	return {books, collections, creators};
};
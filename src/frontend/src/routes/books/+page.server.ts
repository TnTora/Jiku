export const load = async () => {
    let res = await fetch(`http://127.0.0.1:8000/books/books_info`);
	let books = await res.json();
    res = await fetch(`http://127.0.0.1:8000/books/collections`);
	let collections = await res.json();
    res = await fetch(`http://127.0.0.1:8000/books/creators`);
	let creators = await res.json();
    console.log(books, collections, creators);
	return {books, collections, creators};
};
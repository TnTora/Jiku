export const load = async () => {
    let res = await fetch("http://127.0.0.1:8000/books/1");
	const book = await res.json();
    res = await fetch("http://127.0.0.1:8000/books/1/p-003");
	const content = await res.json();
    console.log(book);
	return {book, content};
};
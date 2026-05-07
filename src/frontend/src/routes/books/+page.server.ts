export const load = async () => {
    const res = await fetch(`http://127.0.0.1:8000/books/all`);
	const books = await res.json();
    // console.log(books);
	return {books};
};
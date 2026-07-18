<script lang="ts">
    import { onMount } from "svelte";
    import { tick } from "svelte";
    import { getJikuErrorsContext } from "$lib/utils/context.svelte.js";
    import { setEbookReaderOptionsContext } from "./context";
    import { clickOutside } from "$lib/utils/clickOutside.js";
	import TopBar from "./TopBar.svelte";
    import OptionPanel from "./OptionPanel.svelte";
    import SidePanel from "./SidePanel.svelte";
    import BookRender from "./BookRender.svelte";
	import { goto, invalidateAll } from "$app/navigation";
	import TextInputPopup from "$lib/components/TextInputPopup.svelte";
	import { browser } from "$app/environment";
	import ConfirmationPopup from "$lib/components/ConfirmationPopup.svelte";
	import { api_fetch } from "$lib/utils/requests.js";

    let { data } = $props();
    let { book, status_map } = $derived(data);

    const errors = getJikuErrorsContext();


    // svelte-ignore state_referenced_locally
    let curr_section: string = $state(book.last_pos? book.last_pos.section : book.spine[0]);

    let prev_section: string | null = $derived(
        (book.sections[curr_section].number > 0)? book.spine[book.sections[curr_section].number-1]:
        null
    );

    let next_section: string | null = $derived(
        ((book.sections[curr_section].number >= 0) && (book.sections[curr_section].number < book.spine.length-1))?
        book.spine[book.sections[curr_section].number+1]:
        null
    );


    let content = $state("");
    let backward_load = false;

    function loadOptions() {
        let stored;

        if (browser) {
            stored = localStorage.getItem("bookreader_options");
        }
        
        if (stored) {
            return JSON.parse(stored);
        } else {
            return {
                font_size: 20,
                line_height: 2.25,
                vertical: true,
                paginated: true,
                show_progress_bar: true,
                show_progress_tokens: true,
                limit_progress_to_section: true,
            }
        }

    }

    let options = $state(loadOptions());

    $effect(() => {
        localStorage.setItem("bookreader_options", JSON.stringify(options));
    });

    setEbookReaderOptionsContext(options);

    let show_options = $state(false);
    let show_side_panel = $state(false);
    let show_jump_to = $state(false);
    let jump_to_value = $state(0)

    let bookmarking = $state(false);
    let show_bookmarking_confirmation = $state(false);
    let bookmark_selection: number | null = null;
    let bookmark_selection_name: string | null = $state(null);
    let bookmark_selection_preview: string | null = null;

    let show_completion_confirmation = $state(false);

    let book_container: HTMLDivElement;
    let book_container_height: number = $state(0);
    let book_container_width: number = $state(0);

    let book_container_inline_offset: number = $derived(
        options.vertical? book_container_height:
        book_container_width
    );

    let book_container_block_offset: number = $derived(
        options.vertical? book_container_width:
        book_container_height
    );

    
    let page_first_token_span: HTMLSpanElement | null;
    let skip_intersection: boolean = false;

    // svelte-ignore state_referenced_locally
    let stylesheets_elements = new Array<HTMLLinkElement>(book.stylesheets.length);

    $effect(() => {
        console.log(book);
        console.log(prev_section, next_section);

        stylesheets_elements.forEach((el) => {
            if (!el) {return};

            if (book.sections[curr_section].stylesheets.includes(el.getAttribute("data-file"))) {
                el.disabled = false;
            } else {
                el.disabled = true;
            }
        });

    });

    let section_page: number = 0;

    // console.log(curr_section);

    // svelte-ignore state_referenced_locally
    let curr_token_abs: number = $state(book.sections[curr_section].start_tok);
    let curr_token_rel: number = $derived(curr_token_abs - book.sections[curr_section].start_tok);
    let curr_token: number = $derived(options.limit_progress_to_section? curr_token_rel: curr_token_abs);
    let total_tokens: number = $derived(
        (options.limit_progress_to_section && next_section)? book.sections[next_section].start_tok - book.sections[curr_section].start_tok:
        book.total_tokens
    );


    let book_container_scrollPercent: number = $derived(
        (curr_token/total_tokens)*100
    );


    async function loadSectionContent(name:string) {
        const res = await fetch(`/api_bridge/books/id/${book.id}/${name}`);
        curr_section = name;
	    content = await res.json();
    }


    let pageScrollParam = $derived(
        options.vertical? (top:number) => { return {top: top} } :
        (left:number) => { return {left: left} }
    );


    let getInlineOffset = $derived(
        options.vertical? (el: HTMLElement) => { return el.offsetTop } :
        (el: HTMLElement) => { return el.offsetLeft }
    );

    let getBlockOffset = $derived(
        options.vertical? (el: HTMLElement) => { return el.offsetLeft } :
        (el: HTMLElement) => { return el.offsetTop }
    );

    let getScrollPosition = $derived(
        options.vertical? (el: HTMLElement) => { return el.scrollTop } :
        (el: HTMLElement) => { return el.scrollLeft }
    )

    let getScrollLength = $derived(
        options.vertical? (el: HTMLElement) => { return el.scrollHeight } :
        (el: HTMLElement) => { return el.scrollWidth }
    )


    function scrollToPosition(scroll_position: number) {
        book_container.scrollTo(
            pageScrollParam(Math.floor(scroll_position / book_container_inline_offset) * book_container_inline_offset)
        );
    }


    function nextPage(){
        skip_intersection = false;
        // console.log(getScrollPosition(book_container)+book_container_inline_offset, getScrollLength(book_container));
        const next_position = getScrollPosition(book_container)+book_container_inline_offset;
        // console.log(next_position, next_section);
        if (Math.ceil(next_position) >= getScrollLength(book_container)) {
            if (next_section) {
                backward_load = false;
                loadSectionContent(next_section);
            } else {
                show_completion_confirmation = true;
            }
        } else {
            // book_container.scrollBy(pageScrollParam(book_container_inline_offset));
            scrollToPosition(next_position);
        }
    }

    function prevPage(){
        skip_intersection = false;
        // console.log(getScrollPosition(book_container)-book_container_inline_offset, getScrollLength(book_container));

        const next_position = getScrollPosition(book_container)-book_container_inline_offset;
        if ((next_position < 0) && prev_section) {
            backward_load = true;
            loadSectionContent(prev_section);
        } else { 
            // book_container.scrollBy(pageScrollParam(-book_container_inline_offset));
            scrollToPosition(next_position);
        }
    }


    let intersection_observer: IntersectionObserver;
    let resize_observer: ResizeObserver;

    function observeFirstColElements_paginated(){
        const elements = book_container.querySelectorAll("span[data-tok]") as NodeListOf<HTMLSpanElement>;
        let previous_offset: number = 0;

        elements.forEach(el => {
            const curr_offset = getInlineOffset(el as HTMLElement);
            // console.log(el, curr_offset);

            if (curr_offset >= previous_offset) {
                // console.log(el, curr_offset, previous_offset);
                intersection_observer.observe(el);
                previous_offset = Math.ceil(curr_offset / book_container_inline_offset) * book_container_inline_offset;
            }
        });

        // console.log(intersection_observer);
    }

    function observeFirstColElements_scroll(){
        const elements = book_container.querySelectorAll("span[data-tok]") as NodeListOf<HTMLSpanElement>;
        let previous_offset: number = 0;

        elements.forEach(el => {
            const curr_offset = Math.abs(getBlockOffset(el as HTMLElement));
            // console.log("scroll", el, curr_offset);

            if (curr_offset >= previous_offset) {
                // console.log("scroll", el);
                intersection_observer.observe(el);
                previous_offset = Math.ceil(curr_offset / book_container_inline_offset) * book_container_block_offset;
            }
        });

        // console.log(intersection_observer);
    }
    

    let observeFirstColElements = $derived(
        options.paginated? observeFirstColElements_paginated:
        options.show_progress_bar? observeFirstColElements_scroll:
        () => {}
    )


    function handleInitialSetup() {
        page_first_token_span = book.last_pos?.tok_pos?
                                book_container.querySelector(`span[data-tok='${book.last_pos.tok_pos}'`):
                                null;

        console.log(page_first_token_span);

        intersection_observer = new IntersectionObserver(entries => {
            entries.forEach(entry => {
                if (entry.isIntersecting && !skip_intersection) {
                    page_first_token_span = entry.target as HTMLParagraphElement;
                    curr_token_abs = Number(entry.target.getAttribute("data-tok"));

                    // console.log(page_first_token_span);
                }
            })
        }, {
            root: book_container,
            threshold: 1,
        });
    
        let resize_timeout: NodeJS.Timeout;
        resize_observer = new ResizeObserver(entries => {
            if (!book_container) {return}

            intersection_observer.disconnect();
            console.log("resizing");
            if (page_first_token_span) {
                console.log("jumping to ", page_first_token_span);
                book_container_height = book_container.getBoundingClientRect().height;
                book_container_width = book_container.getBoundingClientRect().width;
                scrollToPosition(getInlineOffset(page_first_token_span));
            }
            clearTimeout(resize_timeout);
            resize_timeout = setTimeout(() => {
                skip_intersection = true;
                book_container_height = book_container.getBoundingClientRect().height;
                book_container_width = book_container.getBoundingClientRect().width;
                observeFirstColElements();


                if (!options.paginated) {
                    function activateObserver() {
                        skip_intersection = false;
                        book_container.removeEventListener("scroll", activateObserver)
                    };

                    book_container.addEventListener("scroll", activateObserver);
                }
            }, 100);
        });

        resize_observer.observe(book_container);
    }


    async function loadInitialSection() {
        if (book.last_pos) {
            await loadSectionContent(book.last_pos.section);
            if (book.last_pos.tok_pos) {
                console.log("last_pos: ", book.last_pos.tok_pos);
                await jumpToToken(book.last_pos.tok_pos);
            }
        } else {
            await loadSectionContent(book.spine[0]);
        }
    }

    function startBookmarking() {
        if (show_bookmarking_confirmation) {return}

        bookmarking = true;

        function handleClick(event: Event) {
            console.log(event);
            const selected_token = (event.target as HTMLElement)?.getAttribute("data-tok");
            if (selected_token) {
                // console.log("selected", selected_token);
                bookmark_selection = Number(selected_token);
                let parent_p = (event.target as HTMLElement)?.parentElement;
                while (parent_p && parent_p.getAttribute("data-char-start") === null) {
                    parent_p = parent_p.parentElement
                }
                bookmark_selection_preview = parent_p?.textContent?? null;
                show_bookmarking_confirmation = true;
            }
            bookmarking = false;
            document.removeEventListener("click", handleClick, true);
        };

        document.addEventListener("click", handleClick, true);
    };

    async function addBookmark() {
        console.log(bookmark_selection_name);
        if (!bookmark_selection_name) { return; }

        let new_bookmark;

        try {
            const res = await api_fetch("books/add_bookmark", {
                method: "POST",
                headers: {
                    "accept": "application/json",
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({
                    book_id: book.id,
                    name: bookmark_selection_name,
                    preview: bookmark_selection_preview,
                    section: curr_section,
                    tok_pos: bookmark_selection,
                })
                }, {
                    err_msg: "Failed to add Bookmark",
                    err_context: errors,
            });
            new_bookmark = await res.json();
        } catch (error) {
            throw error;
        }

        book.bookmarks.push(new_bookmark);
    }

    function cancelBookmarking() {
        show_bookmarking_confirmation = false;
        bookmark_selection_name = null;
        bookmark_selection_preview = null;
        bookmark_selection = null;
    }

    async function setBookCompleted() {
        await api_fetch("books/set_progress_status", {
                method: "PUT",
                headers: {
                    "accept": "application/json",
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({
                    id: book.id,
                    new_status: "completed",
                })
            }, {
                err_msg: "Failed to set book as completed",
                err_context: errors,
        });

        show_completion_confirmation = false;
    }

    function onBookContentUpdate() {
        if (!intersection_observer) {return}

        if (backward_load) {
            // scrollToPosition(getScrollLength(book_container));
            book_container.scrollTo(book_container.scrollWidth, book_container.scrollHeight);
        } else {
            // scrollToPosition(0);
            book_container.scrollTo(0, 0);
        }

        intersection_observer.disconnect();
        observeFirstColElements();
        curr_token_abs = book.sections[curr_section].start_tok;
    }

    async function jumpToToken(token: number) {
        if (token <= 0 || token > book.total_tokens) {
            return;
        }

        let start = 0;
        let end = book.spine.length - 1;
        let section: string = curr_section;

        // console.log(start, end);

        while (start <= end) {
            let mid = start + Math.floor((end-start)/2);
            // console.log(start, end);
            // console.log("mid", mid, book.sections[book.spine[mid]].key, book.sections[book.spine[mid]].start_tok);
            if (book.sections[book.spine[mid]].start_tok > token) {
                end = mid - 1;
            } else {
                section = book.sections[book.spine[mid]].key;
                start = mid + 1;
            }
        }

        // console.log(token, section);

        if (section != curr_section) {
            await loadSectionContent(section);
        }

        await tick();

        let token_span = book_container.querySelector(`span[data-tok='${token}'`);

        if (!token_span) { return };
        // console.log(token_span);
        if (options.paginated) {
            scrollToPosition(getInlineOffset(token_span as HTMLElement));
        } else {
            token_span.scrollIntoView();
        }
        curr_token_abs = token;

    }


    async function handleClose() {
        console.log(page_first_token_span);
        if (page_first_token_span) {
            let tok_position = page_first_token_span.getAttribute("data-tok");
            
            await api_fetch("books/update_last_pos", {
                    method: "PUT",
                    headers: {
                        "accept": "application/json",
                        "Content-Type": "application/json",
                    },
                    body: JSON.stringify({
                        id: book.id,
                        section: curr_section,
                        tok_pos: tok_position,
                    }),
                    keepalive: true
                }, {
                    err_msg: `Failed to update book ${book.id} last_pos: `,
                    err_context: errors,
            });

            invalidateAll();
        }
    }


    function createStatusStyle() {
        const status_style: HTMLStyleElement = document.createElement("style");
        document.head.appendChild(status_style);
        
        const status_sheet: CSSStyleSheet | null = status_style.sheet;

        for ( let [lemma, status] of Object.entries(status_map)) {
            status_sheet?.insertRule(`
                .tok-${lemma} {
                    --c: ${(status == 1)? "var(--known-color)" : "var(--new-color)"} !important;
                }
            `);
        }

        return status_style;
    }


    async function update_last_open() {
        console.log(`updating last opened: ${book.id}`);
        await fetch(`/api_bridge/books/update_last_opened`, {
            method: "PUT",
            headers: {
                "accept": "application/json",
                "Content-Type": "application/json",
            },
            body: JSON.stringify({
                id: book.id
            })
        })
    }


    let status_style: HTMLStyleElement;

    onMount(() => {
        console.log(book_container);
        page_first_token_span = null;

        book_container_height = book_container.getBoundingClientRect().height;
        book_container_width = book_container.getBoundingClientRect().width;
        
        loadInitialSection()
        .then(handleInitialSetup);

        status_style = createStatusStyle();
        // console.log("sheet", status_style.sheet);
        update_last_open();

        return handleClose;
    });
</script>

<svelte:window 
    onbeforeunload = {handleClose}
></svelte:window>

<svelte:head>
    <!-- <link rel="stylesheet" type="text/css" href="/api_bridge/static/shared/morph_status.css"> -->
    {#each book.stylesheets as sheet_file, i}
        <link bind:this={stylesheets_elements[i]} rel="stylesheet" type="text/css" href="/api_bridge/static/books/{book.id}/stylesheets/{sheet_file}" data-file="{sheet_file}" disabled>
    {/each}
</svelte:head>


<div class="flex flex-col h-screen w-screen">
    <TopBar title={book.title}
            toggleOptions={() => {show_options = !show_options}}
            toggleSidePanel={() => {show_side_panel = !show_side_panel}}
            toggleJumpBox={() => {show_jump_to = !show_jump_to}}
            toggleBookmarking={startBookmarking}
    />

    <div class="flex-1 h-(--reader-height) relative" style="--reader-height: calc(100vh - 3rem);">

        {#if show_options}
            <OptionPanel onoutsideclick={() => { show_options = false }} />
        {/if}

        {#if show_side_panel}
            <SidePanel
                {book}
                onoutsideclick={() => { show_side_panel = false }} 
                updatePosition={async (section: string, token?: number, anchor?: string) => {
                    backward_load = false;
                    if (section != curr_section) {
                        await loadSectionContent(section);
                        curr_token_abs = book.sections[section].start_tok;
                    }

                    await tick();

                    if (token) {
                        let token_span = book_container.querySelector(`span[data-tok='${token}'`);
                        // console.log(token_span);
                        if (options.paginated) {
                            scrollToPosition(getInlineOffset(token_span as HTMLElement));
                        } else {
                            token_span?.scrollIntoView();
                        }
                        
                        curr_token_abs = token;
                    } else if (anchor) {
                        let anchor_el = book_container.querySelector(`#${anchor}`);

                        if (options.paginated) {
                            scrollToPosition(getInlineOffset(anchor_el as HTMLElement));
                        } else {
                            anchor_el?.scrollIntoView();
                        }

                    } else {
                        scrollToPosition(0);
                    }
                }}
            />
        {/if}

        {#if show_jump_to}
            <div use:clickOutside={"button[title='Jump To']"}
                onoutsideclick={() => {show_jump_to = false}}
                class="absolute w-40 top-2 right-3 z-20 bg-[#1B1B1B] border border-neutral-900 rounded-2xl flex flex-col items-center justify-evenly gap-3 py-3"
            >
                <span>Jump To Token</span>
                <div class="flex flex-col items-center gap-0.5">
                    <input bind:value={jump_to_value} type="number" class="w-25 bg-neutral-800 rounded-md text-center hide-input-spinners">
                    <span class="text-xs text-neutral-400">of {book.total_tokens}</span>
                </div>
                <button
                    title="Jump"
                    class="px-3 py-1 bg-neutral-800 rounded-full text-sm font-semibold cursor-pointer hover:bg-neutral-700 active:bg-neutral-600"
                    onclick={() => {
                        show_jump_to = false;
                        jumpToToken(jump_to_value);
                    }}
                >
                    Jump
                </button>
            </div>
        {/if}


        {#if show_bookmarking_confirmation}
            <TextInputPopup
                bind:text_input_value={bookmark_selection_name}
                text_input_default={`Bookmark ${book.bookmarks.length + 1}`}
                text="Choose a name"
                onCancel={cancelBookmarking}
                onOk={() => {
                    addBookmark();
                    cancelBookmarking();
                }}
            />
        {/if}


        {#if show_completion_confirmation}
            <ConfirmationPopup
                text="You have reached the end of the book. Mark it as completed?"
                onOk={setBookCompleted}
                onCancel={() => {
                    show_completion_confirmation = false;
                }}
            />
        {/if}


        {#if options.paginated}
            <!-- Left Arrow -->
            <button 
                onclick={options.vertical? nextPage : prevPage}
                aria-label={options.vertical? "Next Page" : "Previous Page"}
                class="w-12 absolute left-0 flex items-center justify-center text-neutral-500 hover:bg-linear-[to_right,#333,transparent] h-full z-10"
            >
                <svg class="w-6" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20">
                    <path fill="currentColor" d="m4 10l9 9l1.4-1.5L7 10l7.4-7.5L13 1z" />
                </svg>
            </button>
            <!-- Right Arrow -->
            <button
                onclick={options.vertical? prevPage : nextPage}
                aria-label={options.vertical? "Previous Page" : "Next Page"}
                class="w-12 absolute right-0 flex items-center justify-center text-neutral-500 hover:bg-linear-[to_left,#333,transparent] h-full z-10"
            >
                <svg class="w-6" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20">
                    <path fill="currentColor" d="M7 1L5.6 2.5L13 10l-7.4 7.5L7 19l9-9z" />
                </svg>
            </button>
        {:else}
            <div class="flex gap-1 items-center fixed {options.vertical? "left-4 bottom-11" : "-right-2 bottom-17 -rotate-90"}">
                <button
                    title="Next Section"
                    aria-label="Next Section"
                    class="w-8 h-8 bg-neutral-900/98 hover:bg-neutral-700 active:bg-neutral-600 flex items-center justify-center rounded-l-lg"
                    onclick={() => {
                        if (!next_section) {return};
                        backward_load = false;
                        loadSectionContent(next_section);
                    }}
                >
                    <svg class="w-6" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20">
                        <path fill="currentColor" d="m4 10l9 9l1.4-1.5L7 10l7.4-7.5L13 1z" />
                    </svg>
                </button>

                <button
                    title="Previous Section"
                    aria-label="Previous Section"
                    class="w-8 h-8 bg-neutral-900/98 hover:bg-neutral-700 active:bg-neutral-600 flex items-center justify-center rounded-r-lg"
                    onclick={() => {
                        if (!prev_section) {return};
                        backward_load = true;
                        loadSectionContent(prev_section);
                    }}
                >
                    <svg class="w-6" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20">
                        <path fill="currentColor" d="M7 1L5.6 2.5L13 10l-7.4 7.5L7 19l9-9z" />
                    </svg>
                </button>
            </div>
        {/if}



        <div
            bind:this={book_container}
            id="jiku-book-container"
            class="{bookmarking? "bookmarking": ""} {options.vertical? "vert-rl" : "horz-tb"} {options.paginated? "paginated overflow-hidden": "overflow-scroll! p-12"} w-[calc(100%-2*var(--book-x-margin))]! bg-neutral-800!" 
            style="--forced-line-height: {options.line_height}; font-size: {options.font_size}px; {options.paginated? "": "--book-x-margin: 0rem; --book-margin-top: 0rem; --book-margin-bottom: 0rem;"}"
        >
            {#if content}
                <BookRender {content} onUpdateCallback={onBookContentUpdate}/>
            {:else}
                <div class="w-screen h-screen flex items-center justify-center">
                    <div>Loading...</div>
                </div>
            {/if}
        </div>


        <div class="h-9 w-full fixed bottom-0 z-10 bg-neutral-800/98">
            {#if bookmarking}
                <div class="absolute w-full z-20 text-neutral-400 top-0 text-center text-lg">
                    Select Bookmark starting position
                </div>
            {/if}
            {#if options.show_progress_tokens}
                <div class="absolute rounded text-neutral-500 h-full {options.vertical? "left-2": "right-2"} flex items-center">
                    <span>
                        {curr_token} / {total_tokens}
                    </span>
                </div>
            {/if}
            {#if options.show_progress_bar}
                <div 
                    class="h-2 {options.limit_progress_to_section? "bg-mist-700": "bg-emerald-800"} absolute bottom-0 {options.vertical? "right-0 rounded-l-full": "left-0 rounded-r-full"} transition-[width] duration-200"
                    style="width:{book_container_scrollPercent}%"
                ></div>
            {/if}
        </div>

    </div>
</div>

<style>
    :root {
        --forced-line-height: 2;
        --reader-height: calc(100vh - 3rem);
    }

    :global .bookmarking span:hover{
        background-color: rgb(215, 50, 0) !important;
        cursor:crosshair;
        border-radius: 0.5rem;
        border: 1rem;
    }

    :global #jiku-book-container p {
        line-height: var(--forced-line-height) !important;
    }

    :global #jiku-book-container img,
    :global #jiku-book-container image,
    :global #jiku-book-container svg {
        max-height: var(--book-container-height) !important;
    }

    :global .jiku-book-body,
    :global .jiku-book-html {
        background-color: var(--color-neutral-800) /* oklch(26.9% 0 0) = #262626 */ !important;
        color: var(--color-neutral-200) !important;
    }

    #jiku-book-container {
        --book-x-margin: 3rem;
        --book-margin-top: 1rem;
        --book-margin-bottom: 3rem;
        --book-container-height: calc(var(--reader-height) - var(--book-margin-top) - var(--book-margin-bottom));
        margin-top: var(--book-margin-top);
        margin-left: var(--book-x-margin);
        margin-right: var(--book-x-margin);
        height: var(--book-container-height);
        max-height: var(--book-container-height)
    }

    @media screen and (width <= 900px) {
        .paginated:not(.vert-rl) {
            --custom-gap: 0rem;
            column-gap: var(--custom-gap);
            /* column-width: calc(50vw - var(--book-x-margin) - var(--custom-gap)); */
            column-count: 1;
            padding-inline: calc(var(--custom-gap) / 2);
        }
    }

    @media screen and (width > 900px) {
        .paginated:not(.vert-rl) {
            --custom-gap: 3rem;
            column-gap: var(--custom-gap);
            /* column-width: calc(50vw - var(--book-x-margin) - var(--custom-gap)); */
            column-count: 2;
            padding-inline: calc(var(--custom-gap) / 2);
        }
    }

    .paginated.vert-rl {
        --custom-gap: 0rem;
        column-gap: var(--custom-gap);
        /* column-width: calc(100vh - var(--custom-gap)); */
        column-count: 1;
        padding-inline: calc(var(--custom-gap) / 2);
    }

    /* .paginated {
        margin-left: var(--book-x-margin);
        margin-right: var(--book-x-margin);
    } */


</style>

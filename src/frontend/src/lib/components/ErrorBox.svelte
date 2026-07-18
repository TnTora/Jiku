<script lang="ts">
	import { getJikuErrorsContext } from '$lib/utils/context.svelte';

    // let { errors } = $props();

    const errors_context = getJikuErrorsContext();

    let hover_options: boolean = $state(false);
    let show_all: boolean = $state(false);

    function onclick () {
        errors_context.errors.pop();
    }

</script>

{#if errors_context.errors.length > 0}
    {#if show_all}
        <div class="w-screen h-screen fixed top-0 left-0 bg-neutral-800/90 z-49"></div>
    {/if}

    <div
        class="min-w-2xs max-w-[500px] fixed top-3 z-50 left-[50%] -translate-x-[50%]"
        role="presentation"
        onmouseleave={() => { hover_options = false;}}
    >
        {#if show_all}
            <div
                class="scroll-box max-h-[75vh] py-3 overflow-y-scroll flex flex-col gap-3 justify-between"
                {@attach (element) => {
                    element.scrollTo({top: element.scrollHeight});
                }}
            >
                {#each errors_context.errors as error }
                    <div class="w-full p-3 bg-red-500 border border-red-300 rounded-3xl text-white text-center">
                        {error.short}
                    </div>
                {/each}
            </div>
        {:else}
            <div 
                class=" min-h-12 py-2 bg-red-500 border border-red-300 rounded-3xl text-white grid grid-cols-[1fr_auto_1fr] grid-rows-[1fr_auto_1fr] items-center gap-x-1.5"
                role="presentation"
                onmouseenter={() => { hover_options = true; }}
            >
                <div class="row-span-full col-start-1 flex">
                    <div class="ml-3 px-2 bg-red-300 min-w-6 rounded-full">{errors_context.errors.length}</div>
                </div>
                <div class="row-[1/4] col-start-2 mx-2 text-center">
                    <div class="text-sm ">{errors_context.errors[errors_context.errors.length-1].short?? "Error"}</div>
                </div>
                <div class="row-span-full col-start-3 flex justify-end">
                    <button title="Close" {onclick} class="mr-5 hover:text-neutral-700 hover:cursor-pointer">
                        <svg xmlns="http://www.w3.org/2000/svg" class="h-5" viewBox="0 0 15 15">
                            <path fill="currentColor" d="M3.64 2.27L7.5 6.13l3.84-3.84A.92.92 0 0 1 12 2a1 1 0 0 1 1 1a.9.9 0 0 1-.27.66L8.84 7.5l3.89 3.89A.9.9 0 0 1 13 12a1 1 0 0 1-1 1a.92.92 0 0 1-.69-.27L7.5 8.87l-3.85 3.85A.92.92 0 0 1 3 13a1 1 0 0 1-1-1a.9.9 0 0 1 .27-.66L6.16 7.5L2.27 3.61A.9.9 0 0 1 2 3a1 1 0 0 1 1-1c.24.003.47.1.64.27" />
                        </svg>
                    </button>
                </div>
                {#if errors_context.errors[errors_context.errors.length-1].details}
                    <div class="row-start-2 col-start-2 text-center">{false? errors_context.errors[errors_context.errors.length-1].details: ""}</div>
                    <div class="row-start-3 col-start-2 text-[0.5rem] h-full text-center flex flex-col justify-end ">
                        <div class="hover:text-neutral-700 hover:cursor-pointer">Show Details</div>
                    </div>
                {/if}
            </div>
        {/if}

        {#snippet hover_button(text: string, callback: () => void = () => {})}
            <button
                class="text-shadow-black text-shadow-lg hover:text-sky-500 active:text-sky-400"
                onclick={callback}
            >
                {text}
            </button>
        {/snippet}

        {#if show_all}
            <div class="mt-3 flex justify-center items-center gap-4 text-xs">
                {@render hover_button("Hide", () => { show_all = false;})}
                {@render hover_button("Close all", () => {
                    show_all = false;
                    errors_context.errors.length = 0;
                })}
            </div>
        {:else if hover_options}
            <div class="mt-0.75 pb-2 flex justify-center items-center gap-4 text-xs">
                {@render hover_button("Show all", () => { show_all = true;})}
                {@render hover_button("Close all", () => { errors_context.errors.length = 0; })}
            </div>
        {/if}
    </div>
{/if}

<style>
    .scroll-box {
        --fade-amount: 15px;
        mask-image: linear-gradient(to bottom, transparent, black var(--fade-amount), black calc(100% - var(--fade-amount)), transparent);
    }
</style>
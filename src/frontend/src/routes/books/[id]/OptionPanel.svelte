<script lang="ts">
    import { getEbookReaderOptionsContext, type EbookReaderOptionsBooleanKey } from "./context";
    import Toggle from "$lib/components/Toggle.svelte";
    import SelectOption from "$lib/components/SelectOption.svelte";
    import { clickOutside } from "$lib/utils/clickOutside.js";


    let { onoutsideclick }: {onoutsideclick: () => void} = $props();
    let options = getEbookReaderOptionsContext();
    const header_style = "col-span-2 text-xl font-bold mt-4";

    function toggleOption(option: EbookReaderOptionsBooleanKey) {
        const handle = () => { options[option] = !options[option] };
        return handle;
    }
</script>

<div
    use:clickOutside={"button[title=Options]"}
    {onoutsideclick}
    class="w-100 max-w-screen grid grid-cols-[auto_auto] items-center justify-between gap-2 px-4 py-4 absolute top-2 right-3 z-20 bg-[#1B1B1B] border border-neutral-900 rounded-2xl"
>
    <h2 class="{header_style}" style="margin-top:0;">Layout</h2>

    <div class="col-span-2">
        <SelectOption bind:selected_value={options.vertical} options={[{name: "Vertical", value: true}, {name: "Horizontal", value: false}]} --height="2rem" />
    </div>

    <div class="col-span-2">
        <SelectOption bind:selected_value={options.paginated} options={[{name: "Paginated", value: true}, {name: "Scroll", value: false}]} --height="2rem" />
    </div>

    <h2 class="{header_style}">Style</h2>

    <label for="font_size">Font Size</label>
    <div class="flex items-center mx-auto border border-neutral-600 bg-neutral-600 rounded-full">
        <button onclick={() => { options.font_size-- }} class="w-7 h-7 pl-1 text-[0.7rem] rounded-l-full cursor-pointer bg-neutral-700 active:bg-neutral-600">A</button>
        <input id="font_size" type="number" bind:value={options.font_size} class="w-9 h-7 text-sm text-center hide-input-spinners z-10">
        <button onclick={() => { options.font_size++ }} class="w-7 h-7 pr-1 text-[1rem] rounded-r-full cursor-pointer bg-neutral-700 active:bg-neutral-600">A</button>
    </div>

    <label for="line_height">Line Height</label>
    <div class="flex items-center mx-auto border border-neutral-600 bg-neutral-600 rounded-full">
        <button onclick={() => { options.line_height -= 0.25 }} class="w-7 h-7 pl-1 rounded-l-full cursor-pointer bg-neutral-700 active:bg-neutral-600">-</button>
        <input id="line_height" type="number" bind:value={options.line_height} class="w-9 h-7 text-sm text-center hide-input-spinners z-10">
        <button onclick={() => { options.line_height += 0.25 }} class="w-7 h-7 pr-1 rounded-r-full cursor-pointer bg-neutral-700 active:bg-neutral-600">+</button>
    </div>


    <h2 class="{header_style}">Extra</h2>

    <span>Show Progress Bar</span>
    <div class="toggle">
        <Toggle option={options.show_progress_bar} title={"Show Progress Bar"} height={1.25}  onclick={toggleOption("show_progress_bar")}/>
    </div>

    <span>Show Tokens Progress</span>
    <div class="toggle">
        <Toggle option={options.show_progress_tokens} title={"Show Tokens Progress"} height={1.25}  onclick={toggleOption("show_progress_tokens")}/>
    </div>

    <div class="col-span-2">
        <SelectOption bind:selected_value={options.limit_progress_to_section} options={[{name: "Section Progress", value: true}, {name: "Book Progress", value: false}]} --height="2rem" />
    </div>

    
    
</div>

<style>

    label, span {
        width: fit-content;
        margin-left:0.5rem;
    }

    /* input {
        width: 2.5rem;
        margin-inline: auto;
    } */

    .toggle {
        margin-inline: auto;
    }

</style>
<script lang="ts">
    import { getEbookReaderOptionsContext, type EbookReaderOptionsBooleanKey } from "./context";
    import Toggle from "$lib/components/Toggle.svelte";
    import SelectOption from "$lib/components/SelectOption.svelte";
    import { clickOutside } from "$lib/utils/clickOutside.js";
	import CustomNumberInput from "$lib/components/CustomNumberInput.svelte";
	import FontSelect from "$lib/components/FontSelect.svelte";


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

    <!-- Layout -->

    <h2 class="{header_style}" style="margin-top:0;">Layout</h2>

    <div class="col-span-2">
        <SelectOption bind:selected_value={options.vertical} options={[{name: "Vertical", value: true}, {name: "Horizontal", value: false}]} --height="2rem" />
    </div>

    <div class="col-span-2">
        <SelectOption bind:selected_value={options.paginated} options={[{name: "Paginated", value: true}, {name: "Scroll", value: false}]} --height="2rem" />
    </div>

    <!-- Style -->

    <h2 class="{header_style}">Style</h2>

    <label for="font">Font</label>

    <FontSelect id="font" bind:value={options.font} class="text-center"/>

    <!-- <label for="custom_font">Custom Font</label>
    <input id="custom_font" type="text" bind:value={options.font}> -->

    <label for="font_size">Font Size</label>

    <CustomNumberInput 
        id="font_size"
        bind:value={options.font_size}
        left_text="A"
        right_text="A"
        left_fn={() => { options.font_size-- }}
        right_fn={() => { options.font_size++ }}
        left_style="font-size: 0.7rem"
    />

    <label for="line_height">Line Height</label>

    <CustomNumberInput 
        id="line_height"
        bind:value={options.line_height}
        left_fn={() => { options.line_height -= 0.25 }}
        right_fn={() => { options.line_height += 0.25 }}
    />

    <!-- Extra -->

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
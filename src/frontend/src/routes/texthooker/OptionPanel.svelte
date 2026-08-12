<script lang="ts">
    import { getTextHookerOptionsContext } from "./context";
    import { clickOutside } from "$lib/utils/clickOutside.js";
    import SelectOption from "$lib/components/SelectOption.svelte";
	import CustomNumberInput from "$lib/components/CustomNumberInput.svelte";
	import FontSelect from "$lib/components/FontSelect.svelte";

    interface Props {
        onoutsideclick: () => void,
        presets: string[],
        preset_name: string,
    }

    let { onoutsideclick, presets, preset_name = $bindable() }: Props = $props();
    let options = getTextHookerOptionsContext();
</script>

<div use:clickOutside={"button[title=Options]"} {onoutsideclick} class="w-100 max-w-screen grid grid-cols-2 items-center justify-between gap-2 px-4 py-4 fixed top-13 right-3 z-9 bg-mist-800 border-mist-900 border rounded-xl">
    
    <!-- Main settings -->

    <h2 class="col-span-2 text-xl font-bold mt-4" style="margin-top:0;">Main</h2>
    
    <label for="preset">Preset</label>
    <select id="preset" bind:value={preset_name}
        onchange={(event) => {
            const new_preset = (event.target as HTMLSelectElement).value;
            window.location.href = `?preset=${new_preset}`;
        }}
    >
        {#each presets as preset}
            <option value={preset}>{preset}</option>
        {/each}
    </select>
    
    <label for="ws_url">WebSocket URL</label>
    <input id="ws_url" type="text" bind:value={options.websocket_url}>

    <label for="max_repetition">Max line repetition</label>

    <CustomNumberInput 
        id="max_repetition"
        bind:value={options.max_repetition}
        left_fn={() => { options.max_repetition = Math.max(0, options.max_repetition-1) }}
        right_fn={() => { options.max_repetition++ }}
    />
    

    <!-- Layout -->

    <h2 class="col-span-2 text-xl font-bold mt-4">Layout</h2>

    <div class="col-span-2">
        <SelectOption bind:selected_value={options.vertical} options={[{name: "Vertical", value: true}, {name: "Horizontal", value: false}]} --height="2rem" />
    </div>

    <!-- Style -->

    <h2 class="col-span-2 text-xl font-bold mt-4">Style</h2>

    <label for="font">Font</label>

    <FontSelect id="font" bind:value={options.font} class="text-center" />

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
    
</div>

<style>
    label {
        width: fit-content;
        margin-left:0.5rem;
    }
</style>
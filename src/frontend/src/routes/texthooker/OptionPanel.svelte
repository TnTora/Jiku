<script lang="ts">
    import { default_texthooker_options, getTextHookerOptionsContext } from "./context";
    import { clickOutside } from "$lib/utils/clickOutside.js";
    import SelectOption from "$lib/components/SelectOption.svelte";
	import CustomNumberInput from "$lib/components/CustomNumberInput.svelte";
	import FontSelect from "$lib/components/FontSelect.svelte";
	import { getConfirmationPopupContext, getJikuErrorsContext, getTextInputPopupContext } from "$lib/utils/context.svelte";
	import { api_fetch } from "$lib/utils/requests";

    interface Props {
        onoutsideclick: () => void,
        presets: string[],
        preset_name: string,
    }

    let { onoutsideclick, presets, preset_name = $bindable() }: Props = $props();
    let options = getTextHookerOptionsContext();

    let confirmation_popup = getConfirmationPopupContext();
    let text_input_popup = getTextInputPopupContext();
    let errors = getJikuErrorsContext();

    async function deletePreset(name: string) {

        await api_fetch(`texthooker/delete_preset/${name}`, {
            method: "DELETE"
        }, {
            err_msg: "Failed to delete preset",
            err_context: errors,
        })

        await api_fetch(`texthooker/clear_lines/${name}`, {
            method: "DELETE"
        }, {
            err_msg: "Falied to clear lines",
            err_context: errors
        })

        localStorage.removeItem(`texthooker_preset_${name}`);
    }

    async function addPreset(name: string) {
        const preset_ws = options.websocket_url;

        await api_fetch("texthooker/add_preset", {
            method: "POST",
            headers: {
                "accept": "application/json",
                "Content-Type": "application/json",
            },
            body: JSON.stringify({
                name: name,
                ws_url: preset_ws,
            })
        }, {
            err_msg: "Failed to add preset",
            err_context: errors,
        });
    }
</script>

<div use:clickOutside={"button[title=Options]"} {onoutsideclick} class="w-100 max-w-screen grid grid-cols-2 items-center justify-between gap-2 px-4 py-4 fixed top-13 right-3 z-9 bg-mist-800 border-mist-900 border rounded-xl">
    
    <!-- Main settings -->

    <h2 class="col-span-2 text-xl font-bold mt-4" style="margin-top:0;">Main</h2>
    
    <label for="preset">Preset</label>
    
    <div class="flex gap-1 justify-between items-center">
        <select id="preset" bind:value={preset_name}
            class="shrink grow overflow-hidden"
            onchange={(event) => {
                const new_preset = (event.target as HTMLSelectElement).value;
                window.location.href = `?preset=${new_preset}`;
            }}
        >
            {#each presets as preset}
                <option value={preset}>{preset}</option>
            {/each}
        </select>
        <button
            title="add preset"
            class="flex items-center justify-center aspect-square h-6 border border-neutral-600 bg-neutral-700 active:bg-neutral-600 rounded-xs cursor-pointer"
            onclick={() => {
                text_input_popup.text = "Select new preset name";
                text_input_popup.onOk = () => {
                    if (!text_input_popup.text_input_value) { 
                        alert("no preset name");
                        throw new Error("no preset name set");
                    }
                    
                    if (presets.includes(text_input_popup.text_input_value)) { 
                        alert("preset name already in use");
                        throw new Error(`preset name '${text_input_popup.text_input_value}' already in use`);
                    }

                    const new_preset = text_input_popup.text_input_value;

                    addPreset(new_preset).then(
                        () => {
                            const default_options = localStorage.getItem("texthooker_preset_Default")?? JSON.stringify(default_texthooker_options);
                            localStorage.setItem(`texthooker_preset_${new_preset}`, default_options);
                            window.location.href = `?preset=${new_preset}`;
                        }
                    );

                };
                text_input_popup.show = true;
            }}
        >
            <svg xmlns="http://www.w3.org/2000/svg" width="1em" height="1em" viewBox="0 0 1024 1024">
                <path d="M0 0h1024v1024H0z" fill="none" />
                <path fill="currentColor" d="M482 152h60q8 0 8 8v704q0 8-8 8h-60q-8 0-8-8V160q0-8 8-8" />
                <path fill="currentColor" d="M192 474h672q8 0 8 8v60q0 8-8 8H160q-8 0-8-8v-60q0-8 8-8Z" />
            </svg>
        </button>
        {#if (preset_name  !== "Default")}
            <button
                title="delete preset"
                class="flex items-center justify-center aspect-square h-6 border border-neutral-600 bg-neutral-700 active:bg-neutral-600 rounded-xs cursor-pointer text-red-500"
                onclick={() => {
                    confirmation_popup.text = `Delete preset '${preset_name}'?`
                    confirmation_popup.onOk = () => {
                        deletePreset(preset_name).then(
                            () => { window.location.href = "?preset=Default"; }
                        );
                    };
                    confirmation_popup.show = true;
                }}
            >
                <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24">
                    <path fill="currentColor" d="M6 19a2 2 0 0 0 2 2h8a2 2 0 0 0 2-2V7H6zm2.46-7.12l1.41-1.41L12 12.59l2.12-2.12l1.41 1.41L13.41 14l2.12 2.12l-1.41 1.41L12 15.41l-2.12 2.12l-1.41-1.41L10.59 14zM15.5 4l-1-1h-5l-1 1H5v2h14V4z" />
                </svg>
            </button>
        {/if}
    </div>
    
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

    <label for="text-color">Text Color</label>

    <div class="flex justify-center gap-1">
        <input id="text-color-text" type="text" bind:value={options.text_col} class="w-25">
        <input id="text-color" type="color" bind:value={options.text_col} class="h-6 w-6">
        <button
            title="reset text color"
            class="flex items-center justify-center aspect-square h-6 border border-neutral-600 bg-neutral-700 active:bg-neutral-600 rounded-xs cursor-pointer"
            onclick={() => {
                options.text_col = default_texthooker_options.text_col;
            }}
        >
            <svg xmlns="http://www.w3.org/2000/svg" width="1em" height="1em" viewBox="0 0 32 32">
                <path d="M0 0h32v32H0z" fill="none" />
                <path fill="currentColor" d="M18 28A12 12 0 1 0 6 16v6.2l-3.6-3.6L1 20l6 6l6-6l-1.4-1.4L8 22.2V16a10 10 0 1 1 10 10Z" />
            </svg>            
        </button>
    </div>


    <label for="bg-color">BG Color</label>

    <div class="flex justify-center gap-1">
        <input id="bg-color-text" type="text" bind:value={options.bg_col} class="w-25">
        <input id="bg-color" type="color" bind:value={options.bg_col} class="h-6 w-6">
        <button
            title="reset bg color"
            class="flex items-center justify-center aspect-square h-6 border border-neutral-600 bg-neutral-700 active:bg-neutral-600 rounded-xs cursor-pointer"
            onclick={() => {
                options.bg_col = default_texthooker_options.bg_col;
            }}
        >
            <svg xmlns="http://www.w3.org/2000/svg" width="1em" height="1em" viewBox="0 0 32 32">
                <path d="M0 0h32v32H0z" fill="none" />
                <path fill="currentColor" d="M18 28A12 12 0 1 0 6 16v6.2l-3.6-3.6L1 20l6 6l6-6l-1.4-1.4L8 22.2V16a10 10 0 1 1 10 10Z" />
            </svg>            
        </button>
    </div>
    
</div>

<style>
    label {
        width: fit-content;
        margin-left:0.5rem;
    }
</style>
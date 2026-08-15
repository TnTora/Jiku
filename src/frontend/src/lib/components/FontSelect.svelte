<script lang="ts">
	import type { HTMLSelectAttributes } from "svelte/elements";


    // interface Props extends HTMLSelectAttributes {
    //     id: number,
    //     value: string
    // }

    let { id="font", value=$bindable(), ...res }: HTMLSelectAttributes = $props();

    const font_options = [
        {
            name: "DotGothic16",
            value: "'DotGothic16', sans-serif",
        },
        {
            name: "Klee One",
            value: "'Klee One', cursive",
        },
        {
            name: "Noto Sans JP",
            value: "'Noto Sans JP', sans-serif",
        },
        {
            name: "Zen Old Mincho",
            value: "'Zen Old Mincho', serif",
        },
        {
            name: "serif",
            value: "serif",
        },
        {
            name: "sans-serif",
            value: "sans-serif",
        },
        {
            name: "cursive",
            value: "cursive",
        },
        {
            name: "Default",
            value: undefined,
        },
    ];

</script>

<select {id} bind:value={value} {...res}>
    {#each font_options as font_option}
        <option value={font_option.value}>{font_option.name}</option>
    {/each}
</select>
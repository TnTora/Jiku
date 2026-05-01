<script lang="ts">
    let { option, title, height, onclick } = $props()
</script>

<button aria-pressed={option} {onclick} {title} 
    class="rounded-full"
    style="height: {height}rem; width: {2*height}rem">
    <span
        aria-hidden="true"
        style="height: {height-0.2}rem; width: {height-0.2}rem; {option? "right" : "left"}: 0.1rem; top: 0.1rem;"
        class="rounded-full"></span>
</button>

<style>

button {
    position: relative;
    transition-property: background-color;
    transition-duration: 900;
}

button[aria-pressed=true] {
    background-color: #0062ff;
}

button[aria-pressed=false] {
    background-color: #888;
}

span {
    position: absolute;
    display: block;
    background-color: #ccc;
    transition-property: all;
    transition-duration: 100;
}

</style>
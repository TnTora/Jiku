<script lang="ts">
    let { toggleWebSocket, ws_connected, toggleOptions } = $props();
    let ws_conn_color = $derived(ws_connected? "text-green-500": "text-red-500");
    let btn_shared_classes = "mr-3 hover:text-sky-700 active:text-sky-500 hover:cursor-pointer";

</script>

<div class="fixed top-0 right-0 bg-mist-800/90 border-l border-b border-mist-700/90 h-10 px-3 rounded-bl-lg flex items-center z-10">
    <button class="{btn_shared_classes} {ws_conn_color}" onclick={toggleWebSocket} >WS</button>
    <button class="{btn_shared_classes}">Delete last line </button>
    <button class="{btn_shared_classes}">Clear all lines </button>
    <button class="{btn_shared_classes}" onclick={toggleOptions}>Options</button>
</div>

<style>

</style>
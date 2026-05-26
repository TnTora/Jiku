<script lang="ts">
	import './layout.css';
	import favicon from '$lib/assets/favicon.svg';
	import { setJikuErrorsContext } from '$lib/utils/context';
	import { setConfirmationPopupContext, setTextInputPopupContext } from '$lib/utils/context';
	import ErrorBox from '$lib/components/ErrorBox.svelte';
	import ConfirmationPopup from '$lib/components/ConfirmationPopup.svelte';
	import TextInputPopup from '$lib/components/TextInputPopup.svelte';
	import type { ConfirmationPopupContext, TextInputPopupContext } from '$lib/utils/context';


	let { children } = $props();
	// let test_errors = [{short: "test1", details:"test message 1"}, {short: "test2", details:"test message 2"}];
	let errors = $state([]);
	setJikuErrorsContext(errors);


	let confirmation_popup: ConfirmationPopupContext = $state({
		show: false,
		text: "",
		onOk: () => { return; },
		onCancel: () => { return; },
	});

	setConfirmationPopupContext(confirmation_popup);

	let text_input_popup: TextInputPopupContext = $state({
		show: false,
		text: "",
		text_input_value: null,
		text_input_default: "",
		onOk: () => { return; },
		onCancel: () => { return; },
	});

	setTextInputPopupContext(text_input_popup);

	function resetPopContexts() {
        text_input_popup.show= false;
        text_input_popup.text = "";
        text_input_popup.text_input_value = null;

		confirmation_popup.show= false;
        confirmation_popup.text = "";
    }

	function modalOkWrapper(modalFunc: () => any) {
		return () => {
			let res = modalFunc();
			Promise.resolve(res).then(
				resetPopContexts
			);
		}
	}

</script>

<svelte:head><link rel="icon" href={favicon} /></svelte:head>

<ErrorBox {errors} />

{#if confirmation_popup.show}
	<ConfirmationPopup
		text={confirmation_popup.text}
		onCancel={() => {
			confirmation_popup.onCancel();
			resetPopContexts();
		}}
		onOk={modalOkWrapper(confirmation_popup.onOk)}
	/>
{/if}

{#if text_input_popup.show}
	<TextInputPopup 
		bind:text_input_value={text_input_popup.text_input_value}
		text_input_default={text_input_popup.text_input_default}
		text={text_input_popup.text}
		onCancel={() => {
			text_input_popup.onCancel();
			resetPopContexts();
		}}
		onOk={modalOkWrapper(text_input_popup.onOk)}
	/>
{/if}

{@render children()}

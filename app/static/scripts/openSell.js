document.getElementById("sell-open-btn").addEventListener("click", function(){
    document.getElementById("window-convert-sell").classList.add("open")
})


window.addEventListener('keydown', (e) => {
    if (e.key === "Escape") {
        document.getElementById("window-convert-sell").classList.remove("open")
    }
});

document.querySelector("#window-convert-sell .convert").addEventListener('click', event => {
    event._isClickWithInModal = true;
});

document.getElementById("window-convert-sell").addEventListener('click', event => {
    if (event._isClickWithInModal) return;
    event.currentTarget.classList.remove('open');
});
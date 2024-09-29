document.getElementById("buy-open-btn").addEventListener("click", function(){
    document.getElementById("window-convert-buy").classList.add("open")
})


window.addEventListener('keydown', (e) => {
    if (e.key === "Escape") {
        document.getElementById("window-convert-buy").classList.remove("open")
    }
});

document.querySelector("#window-convert-buy .convert").addEventListener('click', event => {
    event._isClickWithInModal = true;
});

document.getElementById("window-convert-buy").addEventListener('click', event => {
    if (event._isClickWithInModal) return;
    event.currentTarget.classList.remove('open');
});
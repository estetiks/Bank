document.getElementById("convert-open-btn").addEventListener("click", function(){
    document.getElementById("window-convert").classList.add("open")
})


window.addEventListener('keydown', (e) => {
    if (e.key === "Escape") {
        document.getElementById("window-convert").classList.remove("open")
    }
});

document.querySelector("#window-convert .convert").addEventListener('click', event => {
    event._isClickWithInModal = true;
});

document.getElementById("window-convert").addEventListener('click', event => {
    if (event._isClickWithInModal) return;
    event.currentTarget.classList.remove('open');
});
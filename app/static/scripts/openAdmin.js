document.getElementById("admin-open-btn").addEventListener("click", function(){
    document.getElementById("window-admin").classList.add("open")
})


window.addEventListener('keydown', (e) => {
    if (e.key === "Escape") {
        document.getElementById("window-admin").classList.remove("open")
    }
});

document.querySelector("#window-admin .remove").addEventListener('click', event => {
    event._isClickWithInModal = true;
});

document.getElementById("window-admin").addEventListener('click', event => {
    if (event._isClickWithInModal) return;
    event.currentTarget.classList.remove('open');
});
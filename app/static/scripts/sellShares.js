document.addEventListener("DOMContentLoaded", function() {
    let firstCurrency = null;
    let secondCurrency = null;

    // Функция для обработки нажатия кнопки валюты
    function handleCurrencyButtonClick(button, group, isFirstCurrency) {
        const buttons = group.querySelectorAll(".shares-btn");
        buttons.forEach(btn => btn.classList.remove("active"));
        button.classList.add("active");

        if (isFirstCurrency) {
            firstCurrency = button.dataset.currency;
        } else {
            secondCurrency = button.dataset.currency;
        }
    }

    const firstCurrencyButtons = document.querySelectorAll('.currency-input:first-of-type .shares-btn');
    firstCurrencyButtons.forEach(button => {
        button.addEventListener('click', function() {
            handleCurrencyButtonClick(this, this.parentElement, true);
        });
    });

    const secondCurrencyButtons = document.querySelectorAll('.currency-input:last-of-type .currency-btn');
    secondCurrencyButtons.forEach(button => {
        button.addEventListener('click', function() {
            handleCurrencyButtonClick(this, this.parentElement, false);
        });

    });

    // Запретить ввод отрицательных чисел
    const firstMoneyInput = document.getElementById("shares");
    firstMoneyInput.addEventListener("input", function() {
        const value = parseFloat(firstMoneyInput.value);
        if (value < 0) {
            firstMoneyInput.value = "";  // Очищаем поле, если введено отрицательное число
            alert("Please enter a positive number.");
        }
    });

});

document.addEventListener("DOMContentLoaded", function() {
    let firstCurrency = null;
    let secondCurrency = null;

    // Функция для обработки нажатия кнопки валюты
    function handleCurrencyButtonClick(button, group, isFirstCurrency) {
        const buttons = group.querySelectorAll(".shares-btn-buy");
        buttons.forEach(btn => btn.classList.remove("active"));
        button.classList.add("active");

        if (isFirstCurrency) {
            firstCurrency = button.dataset.currency;
        } else {
            secondCurrency = button.dataset.currency;
        }

    
        
    }

    const firstCurrencyButtons = document.querySelectorAll('.currency-input:first-of-type .shares-btn-buy');
    firstCurrencyButtons.forEach(button => {
        button.addEventListener('click', function() {
            handleCurrencyButtonClick(this, this.parentElement, true);
        });
    });

    const secondCurrencyButtons = document.querySelectorAll('.currency-input:last-of-type .shares-btn-buy');
    secondCurrencyButtons.forEach(button => {
        button.addEventListener('click', function() {
            handleCurrencyButtonClick(this, this.parentElement, false);
        });
    });

    
    const sharesInput = document.getElementById("shares-buy");
    const moneyInput = document.getElementById("last_money_shares-buy");



    document.querySelector('.calculate-shares-buy').addEventListener('click', function(e) {
        e.preventDefault();


        if (firstCurrency && secondCurrency && sharesInput.value) {

            const validPattern = /^-?\d+$/;
            if (!validPattern.test(sharesInput.value)) {
                alert("Please enter a valid positive integer number.");
                return;
            }

            const amount = parseInt(sharesInput.value);
            

            if (isNaN(amount) || amount < 0) {
                alert("Please enter a valid positive int number.");
                return;
            }


            fetch("/calculate_shares", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({
                    amount: amount,
                    from_currency: firstCurrency,
                    to_currency: secondCurrency
                })
            })
            .then(response => response.json())
            .then(data => {
                document.getElementById("last_money_shares-buy").value = data.output;
            })
            .catch(error => {
                console.error("Error:", error);
            });
        }
    });








    // Отправка данных на сервер для конвертации
    document.querySelector('.convert-shares-buy').addEventListener('click', function(e) {
        e.preventDefault();

        if (firstCurrency && secondCurrency && sharesInput.value && moneyInput.value) {

            const validPattern = /^-?\d+$/;
            if (!validPattern.test(sharesInput.value)) {
                alert("Please enter a valid positive integer number.");
                return;
            }

            const amount = parseInt(sharesInput.value);
            const money = parseFloat(moneyInput.value);
            

            if (isNaN(amount) || amount < 0) {
                alert("Please enter a valid positive integer number.");
                return;
            }



            // AJAX-запрос на сервер Flask
            fetch("/buy_shares", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({
                    amount: money,
                    from_currency: firstCurrency,
                    to_currency: secondCurrency
                })
            })
            .then(response => response.json())
            .then(data => {
                // Получаем результат с сервера и обновляем второе поле
                document.getElementById("last_money_shares-buy").value = data.get;
                if (data.get === 'success!'){
                    window.location.href = '/dashboard';
                }
            })
            .catch(error => {
                console.error("Error:", error);
            });
        }
    });
});
document.addEventListener("DOMContentLoaded", function() {
    const modal = document.getElementById("productInfo");
    const closeModal = document.getElementById("closeModal");
    const productName = document.getElementById("productname");
    const productPrice = document.getElementById("productprice");
    const productImage = document.getElementById("imgbig");
            console.log("222")

     Open modal when product clicked
    document.querySelectorAll(".product__item").forEach(item => {
        item.addEventListener("click", function() {
            console.log("111")

            const name = this.querySelector(".product__name").innerText;
            const price = this.querySelector(".product__price").innerText;
            const imgSrc = this.querySelector(".product__img").getAttribute("src");
            const id = item.getAttribute("id")
            console.log(id)

            productName.innerText = name;
            productPrice.innerText = price;
            productImage.src = imgSrc;

            modal.classList.remove("unactive");
            modal.classList.add("active");
            modal.setAttribute("data-id", id);
        });
    });

    // Close modal
    closeModal.addEventListener("click", function() {
        modal.classList.add("unactive");
        modal.classList.remove("active");
    });
});
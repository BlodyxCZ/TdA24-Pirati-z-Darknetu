var data_cache = null;
var refresh_timeout = null;

document.addEventListener("DOMContentLoaded", () => {
    getLecturers();

    let sliderOne = document.getElementById("price-min");
    let sliderTwo = document.getElementById("price-max");
    let displayValOne = document.getElementById("price-min-value");
    let displayValTwo = document.getElementById("price-max-value");
    let minGap = 0;
    let sliderTrack = document.querySelector(".slider-track");
    let sliderMaxValue = document.getElementById("price-min").max;

    function fillColor() {
        percent1 = (sliderOne.value / sliderMaxValue) * 100;
        percent2 = (sliderTwo.value / sliderMaxValue) * 100;
        sliderTrack.style.background = `linear-gradient(to right, var(--white) ${percent1}% , var(--sunglow) ${percent1}% , var(--sunglow) ${percent2}%, var(--white) ${percent2}%)`;
    }

    sliderOne.addEventListener("input", (e) => {
        if (parseInt(sliderTwo.value) - parseInt(sliderOne.value) <= minGap) {
            sliderOne.value = parseInt(sliderTwo.value) - minGap;
        }
        displayValOne.textContent = sliderOne.value;
        fillColor();
        updateLecturers(data_cache);
        clearTimeout(refresh_timeout);
        refresh_timeout = setTimeout(() => {
            getLecturers();
        }, 500);
    });
    sliderTwo.addEventListener("input", (e) => {
        if (parseInt(sliderTwo.value) - parseInt(sliderOne.value) <= minGap) {
            sliderTwo.value = parseInt(sliderOne.value) + minGap;
        }
        displayValTwo.textContent = sliderTwo.value;
        fillColor();
        updateLecturers(data_cache);
        clearTimeout(refresh_timeout);
        refresh_timeout = setTimeout(() => {
            getLecturers();
        }, 500);
    });

    fillColor();
});

async function getLecturers() {
    console.log("Fetching lecturer list");
    const response = await fetch("/api/lecturers");
    const data = await response.json();
    window.data_cache = data;
    console.log(data);
    updateLecturers(data);
}

function updateLecturers(data) {
    const lecturers = document.getElementById("lecturers");
    lecturers.innerHTML = "";

    let price_min = parseInt(document.getElementById("price-min").value);
    let price_max = parseInt(document.getElementById("price-max").value);

    for (let lecturer of data) {
        if (lecturer.price_per_hour < price_min ||
            lecturer.price_per_hour > price_max) {
            continue;
        }

        const main_container = document.createElement("div");
        main_container.classList.add("split-v");
        const picture_element = document.createElement("img");
        picture_element.src = lecturer.picture_url;
        const picture_container = document.createElement("div");
        picture_container.classList.add("picture-container");
        const name_element = document.createElement("div");
        name_element.classList.add("name");
        name_element.textContent = getName(lecturer);
        const city_element = document.createElement("div");
        city_element.textContent = lecturer.city;
        city_element.classList.add("city");
        const claim_element = document.createElement("div");
        claim_element.classList.add("claim");
        claim_element.textContent = lecturer.claim;
        const tags_list = document.createElement("ul");
        tags_list.classList.add("tags");
        const price_per_hour_element = document.createElement("div");
        price_per_hour_element.classList.add("price-per-hour");
        price_per_hour_element.textContent = `${lecturer.price_per_hour},- Kč / hodina`;

        for (let tag of lecturer.tags) {
            const tag_element = document.createElement("li");
            tag_element.textContent = tag.name;
            tags_list.appendChild(tag_element);
        }

        const split_container = document.createElement("div");

        picture_container.appendChild(picture_element);
        split_container.appendChild(picture_container);
        split_container.appendChild(name_element);
        split_container.appendChild(city_element);
        split_container.appendChild(claim_element);
        split_container.appendChild(tags_list);
        main_container.appendChild(split_container);
        main_container.appendChild(price_per_hour_element);
        lecturers.appendChild(main_container);
    }
}

function getName(lecturer) {
    // Good enough
    return `${lecturer.title_after}${lecturer.title_after != "" ? " " : ""}${lecturer.first_name}${lecturer.middle_name != "" ? " " : ""}${lecturer.middle_name} ${lecturer.last_name}${lecturer.title_before != "" ? " " : ""}${lecturer.title_before}`;
}
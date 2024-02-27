var data_cache = null;
var refresh_timeout = null;

document.addEventListener("DOMContentLoaded", () => {
    getLecturers();
    getLocations();
    getTags();

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

    let locationSelect = document.getElementById("location-select");
    locationSelect.addEventListener("input", (e) => {
        updateLecturers(data_cache);
        clearTimeout(refresh_timeout);
        refresh_timeout = setTimeout(() => {
            getLecturers();
        }, 500);
    });

    let tagSelect = document.getElementById("tag-select");
    tagSelect.addEventListener("change", (e) => {
        let tagList = document.getElementById("tag-list");
        for (let option of tagList.options) {
            if (option.textContent == e.target.value) {
                console.log(option);
                let selected_list = document.getElementById("selected-tags");
                let tag_element = document.createElement("span");
                tag_element.textContent = e.target.value;
                tag_element.addEventListener("click", (e) => {
                    let option_element = document.createElement("option");
                    option_element.textContent = e.target.textContent;
                    tagList.appendChild(option_element);
                    selected_list.removeChild(e.target);

                    updateLecturers(data_cache);
                    clearTimeout(refresh_timeout);
                    refresh_timeout = setTimeout(() => {
                        getLecturers();
                    }, 500);
                });
                selected_list.appendChild(tag_element);
                tagList.removeChild(option);

                tagSelect.value = "";

                updateLecturers(data_cache);
                clearTimeout(refresh_timeout);
                refresh_timeout = setTimeout(() => {
                    getLecturers();
                }, 500);
                break;
            }
        }
    });
});

async function getLecturers() {
    console.log("Fetching lecturer list");
    let response = fetch("/api/lecturers");
    response.catch((err) => {
        setTimeout(() => {
            getLecturers();
        }, 500);
    });
    response.then((res) => {
        const data = res.json();
        data.catch((err) => {
            setTimeout(() => {
                getLecturers();
            }, 500);
        });
        data.then((json) => {
            window.data_cache = json;
            console.log(json);
            updateLecturers(json);
        });
    });
}

function updateLecturers(data) {
    const lecturers = document.getElementById("lecturers");
    lecturers.innerHTML = "";

    for (let lecturer of data) {
        if (check_filter(lecturer)) {
            continue;
        }

        const main_container = document.createElement("a");
        main_container.classList.add("split-v");
        main_container.href = `/lecturer/${lecturer.uuid}`;
        const picture_element = document.createElement("img");
        picture_element.src = lecturer.picture_url;
        const picture_container = document.createElement("div");
        picture_container.classList.add("picture-container");
        const name_element = document.createElement("div");
        name_element.classList.add("name");
        name_element.textContent = getName(lecturer);
        const location_element = document.createElement("div");
        location_element.textContent = lecturer.location;
        location_element.classList.add("location");
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
        split_container.appendChild(location_element);
        split_container.appendChild(claim_element);
        split_container.appendChild(tags_list);
        main_container.appendChild(split_container);
        main_container.appendChild(price_per_hour_element);
        lecturers.appendChild(main_container);
    }
}

function check_filter(lecturer) {
    const price_min = parseInt(document.getElementById("price-min").value);
    const price_max = parseInt(document.getElementById("price-max").value);

    if (lecturer.price_per_hour < price_min ||
        lecturer.price_per_hour > price_max) {
        return true;
    }

    const location = document.getElementById("location-select").value;

    if (location != "" && !lecturer.location.startsWith(location)) {
        return true;
    }

    const tags = document.getElementById("selected-tags").children;

    for (let tag of tags) {
        if (lecturer.tags.find((t) => t.name == tag.textContent) == null) {
            return true;
        }
    }

    return false;
}

function getName(lecturer) {
    // Good enough
    if (lecturer.title_before == null) {
        lecturer.title_before = "";
    }
    if (lecturer.middle_name == null) {
        lecturer.middle_name = " ";
    }
    if (lecturer.title_after == null) {
        lecturer.title_after = "";
    }

    return `${lecturer.title_before}${lecturer.title_before != "" ? " " : ""}${lecturer.first_name}${lecturer.middle_name != "" ? " " : ""}${lecturer.middle_name} ${lecturer.last_name}${lecturer.title_after != "" ? ", " : ""}${lecturer.title_after}`;
}

function getLocations() {
    console.log("Fetching locations");
    if (data_cache == null) {
        setTimeout(() => {
            getLocations();
        }, 500);
        return;
    }
    let data = new Set();
    for (let lecturer of data_cache) {
        data.add(lecturer.location);
    }
    updateLocations(data);
}

function updateLocations(data) {
    const locationSelect = document.getElementById("location-list");
    locationSelect.innerHTML = "";

    for (let location of data) {
        const element = document.createElement("option");
        element.textContent = location;

        locationSelect.appendChild(element);
    }
}

function getTags() {
    console.log("Fetching tags");
    if (data_cache == null) {
        setTimeout(() => {
            getTags();
        }, 500);
        return;
    }
    let data = new Set();
    for (let lecturer of data_cache) {
        for (let tag of lecturer.tags) {
            data.add(tag);
        }
    }
    console.log(data);
    updateTags(data);
}

function updateTags(data) {
    const tag_select = document.getElementById("tag-list");
    tag_select.innerHTML = "";

    for (let tag of data) {
        const element = document.createElement("option");
        element.textContent = tag.name;

        tag_select.appendChild(element);
    }
}
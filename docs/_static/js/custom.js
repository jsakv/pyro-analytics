function addGithubButton() {
    const div = `
        <div class="github-repo">
            <a
                class="github-button"
                href="https://github.com/jsakv/pyro-analytics"
                data-size="large"
                data-show-count="true"
                aria-label="Star jsakv/pyro-analytics on GitHub">Star</a>
        </div>
    `;
    document.querySelector(".sidebar-brand").insertAdjacentHTML("afterend", div);
}

function onLoad() {
    addGithubButton();
}

window.addEventListener("load", onLoad);

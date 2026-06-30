const tabs = document.querySelectorAll("[data-auth-tab]");
const loginForm = document.querySelector("#loginForm");
const registerForm = document.querySelector("#registerForm");
const messageBox = document.querySelector("#authMessage");
const demoLoginBtn = document.querySelector("#demoLoginBtn");

function showMessage(text, danger = false) {
  messageBox.textContent = text;
  messageBox.classList.toggle("danger", danger);
}

function formData(form) {
  return Object.fromEntries(new FormData(form).entries());
}

async function postJson(url, payload) {
  const response = await fetch(url, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  const data = await response.json();
  if (!response.ok) throw new Error(data.error || "请求失败");
  return data;
}

tabs.forEach((tab) => {
  tab.addEventListener("click", () => {
    tabs.forEach((item) => item.classList.remove("active"));
    tab.classList.add("active");
    const isLogin = tab.dataset.authTab === "login";
    loginForm.classList.toggle("hidden", !isLogin);
    registerForm.classList.toggle("hidden", isLogin);
    showMessage("");
  });
});

loginForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  showMessage("正在登录...");
  try {
    await postJson("/api/login", formData(loginForm));
    location.href = "/dashboard";
  } catch (error) {
    showMessage(error.message, true);
  }
});

registerForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  showMessage("正在创建账号...");
  try {
    await postJson("/api/register", formData(registerForm));
    location.href = "/dashboard";
  } catch (error) {
    showMessage(error.message, true);
  }
});

demoLoginBtn.addEventListener("click", async () => {
  showMessage("正在进入演示店铺...");
  try {
    await postJson("/api/demo-login", {});
    location.href = "/dashboard";
  } catch (error) {
    showMessage(error.message, true);
  }
});

const BG_IMAGE_2 = "https://images.higgs.ai/?default=1&output=webp&url=https%3A%2F%2Fd8j0ntlcm91z4.cloudfront.net%2Fuser_38xzZboKViGWJOttwIXH07lWA1P%2Fhf_20260609_201152_bba90a12-bf12-459f-91f0-51f237dbaf3b.png&w=1280&q=85";
const SPOTLIGHT_R = 260;

const canvas = document.querySelector("#spotlightCanvas");
const revealLayer = document.querySelector("#revealLayer");
const ctx = canvas.getContext("2d");

const mouse = { x: -999, y: -999 };
const smooth = { x: -999, y: -999 };
let rafId = 0;

function resizeCanvas() {
  canvas.width = window.innerWidth;
  canvas.height = window.innerHeight;
}

function drawMask() {
  smooth.x += (mouse.x - smooth.x) * 0.1;
  smooth.y += (mouse.y - smooth.y) * 0.1;

  ctx.clearRect(0, 0, canvas.width, canvas.height);
  const gradient = ctx.createRadialGradient(smooth.x, smooth.y, 0, smooth.x, smooth.y, SPOTLIGHT_R);
  gradient.addColorStop(0, "rgba(255,255,255,1)");
  gradient.addColorStop(0.4, "rgba(255,255,255,1)");
  gradient.addColorStop(0.6, "rgba(255,255,255,0.75)");
  gradient.addColorStop(0.75, "rgba(255,255,255,0.4)");
  gradient.addColorStop(0.88, "rgba(255,255,255,0.12)");
  gradient.addColorStop(1, "rgba(255,255,255,0)");

  ctx.fillStyle = gradient;
  ctx.beginPath();
  ctx.arc(smooth.x, smooth.y, SPOTLIGHT_R, 0, Math.PI * 2);
  ctx.fill();

  const mask = `url(${canvas.toDataURL()})`;
  revealLayer.style.maskImage = mask;
  revealLayer.style.webkitMaskImage = mask;
  revealLayer.style.maskSize = "100% 100%";
  revealLayer.style.webkitMaskSize = "100% 100%";

  rafId = requestAnimationFrame(drawMask);
}

function handlePointerMove(event) {
  mouse.x = event.clientX;
  mouse.y = event.clientY;
}

function initHomeHero() {
  revealLayer.style.backgroundImage = `url("${BG_IMAGE_2}")`;
  resizeCanvas();
  window.addEventListener("resize", resizeCanvas);
  window.addEventListener("mousemove", handlePointerMove);
  window.addEventListener("touchmove", (event) => {
    const touch = event.touches[0];
    if (touch) {
      mouse.x = touch.clientX;
      mouse.y = touch.clientY;
    }
  }, { passive: true });
  rafId = requestAnimationFrame(drawMask);
}

window.addEventListener("beforeunload", () => {
  cancelAnimationFrame(rafId);
  window.removeEventListener("resize", resizeCanvas);
  window.removeEventListener("mousemove", handlePointerMove);
});

initHomeHero();

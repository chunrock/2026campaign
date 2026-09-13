/* particles.js — "02 추가검사 항목" 배경의 캔버스 파티클 효과.
   기법 출처: https://techhub.iodigital.com/articles/particle-background-effect-with-canvas
   (파티클 개수 = (w+h)/50, 연결선 반경 = w/10 + h/5, 거리에 따라 선 투명도 감소, 경계에서 반사) */
(function () {
  function initParticles(canvas) {
    var ctx = canvas.getContext("2d");
    var w, h, particles, animId;

    var PARTICLE_COLOR = "200,200,200";
    var LINE_COLOR = "200,200,200";

    function rand(min, max) {
      return Math.random() * (max - min) + min;
    }

    function Particle() {
      this.x = rand(0, w);
      this.y = rand(0, h);
      this.radius = rand(1, 2.4);
      this.speed = rand(0.15, 0.5);
      var angle = rand(0, Math.PI * 2);
      this.vector = { x: Math.cos(angle) * this.speed, y: Math.sin(angle) * this.speed };
    }
    Particle.prototype.update = function () {
      this.x += this.vector.x;
      this.y += this.vector.y;
      if (this.x > w || this.x < 0) this.vector.x *= -1;
      if (this.y > h || this.y < 0) this.vector.y *= -1;
      this.x = Math.min(Math.max(this.x, 0), w);
      this.y = Math.min(Math.max(this.y, 0), h);
    };
    Particle.prototype.draw = function () {
      ctx.beginPath();
      ctx.arc(this.x, this.y, this.radius, 0, Math.PI * 2);
      ctx.fillStyle = "rgba(" + PARTICLE_COLOR + ",0.85)";
      ctx.fill();
    };

    function linkRadius() {
      return w / 10 + h / 5;
    }

    function drawLines() {
      var r = linkRadius();
      for (var i = 0; i < particles.length; i++) {
        for (var j = i + 1; j < particles.length; j++) {
          var dx = particles[i].x - particles[j].x;
          var dy = particles[i].y - particles[j].y;
          var dist = Math.sqrt(dx * dx + dy * dy);
          if (dist < r) {
            var opacity = (1 - dist / r) * 0.5;
            ctx.strokeStyle = "rgba(" + LINE_COLOR + "," + opacity.toFixed(2) + ")";
            ctx.lineWidth = 1;
            ctx.beginPath();
            ctx.moveTo(particles[i].x, particles[i].y);
            ctx.lineTo(particles[j].x, particles[j].y);
            ctx.stroke();
          }
        }
      }
    }

    function resize() {
      var rect = canvas.parentElement.getBoundingClientRect();
      w = canvas.width = rect.width;
      h = canvas.height = rect.height;
      var amount = Math.round((w + h) / 50);
      particles = [];
      for (var i = 0; i < amount; i++) particles.push(new Particle());
    }

    function loop() {
      ctx.clearRect(0, 0, w, h);
      drawLines();
      for (var i = 0; i < particles.length; i++) {
        particles[i].update();
        particles[i].draw();
      }
      animId = requestAnimationFrame(loop);
    }

    resize();
    loop();
    window.addEventListener("resize", resize);
  }

  document.querySelectorAll("canvas.exam-particles").forEach(initParticles);
})();

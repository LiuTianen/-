const canvas = document.getElementById("canvas");
const ctx = canvas.getContext("2d");

canvas.width = window.innerWidth;
canvas.height = window.innerHeight;

let particles = [];

class Particle{
    constructor(x,y){
        this.x = x;
        this.y = y;

        this.size = Math.random()*5+2;

        this.speedX = (Math.random()-0.5)*6;
        this.speedY = (Math.random()-0.5)*6;

        this.alpha = 1;

        this.color = `hsl(${Math.random()*360},100%,70%)`;
    }

    update(){
        this.x += this.speedX;
        this.y += this.speedY;

        this.alpha -= 0.01;
    }

    draw(){
        ctx.globalAlpha = this.alpha;

        ctx.fillStyle = this.color;

        ctx.beginPath();

        ctx.arc(this.x,this.y,this.size,0,Math.PI*2);

        ctx.fill();

        ctx.globalAlpha = 1;
    }
}

function createExplosion(x,y){

    for(let i=0;i<120;i++){
        particles.push(new Particle(x,y));
    }
}

function animate(){

    ctx.fillStyle = "rgba(0,0,0,0.15)";
    ctx.fillRect(0,0,canvas.width,canvas.height);

    for(let i=0;i<particles.length;i++){

        particles[i].update();
        particles[i].draw();

        if(particles[i].alpha <=0){
            particles.splice(i,1);
            i--;
        }
    }

    requestAnimationFrame(animate);
}

animate();

document.getElementById("loveBtn").onclick = ()=>{

    createExplosion(
        canvas.width/2,
        canvas.height/2
    );

    floatingWords();
};

function floatingWords(){

    const words = [
        "我想你",
        "好想你",
        "一直在想你",
        "❤️",
        "Miss You"
    ];

    words.forEach((text,index)=>{

        const div = document.createElement("div");

        div.innerText = text;

        div.style.position = "absolute";
        div.style.left = "50%";
        div.style.top = "50%";

        div.style.color = "white";
        div.style.fontSize = "30px";

        div.style.transition = "3s";

        document.body.appendChild(div);

        setTimeout(()=>{

            div.style.transform =
            `translate(
                ${(Math.random()-0.5)*800}px,
                ${(Math.random()-0.5)*600}px
            )`;

            div.style.opacity = 0;

        },100);

        setTimeout(()=>{
            div.remove();
        },3000);

    });
}

window.addEventListener("click",(e)=>{
    createExplosion(e.clientX,e.clientY);
});
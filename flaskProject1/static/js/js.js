document.addEventListener('DOMContentLoaded', function() {
    const slides = document.querySelectorAll('.slide');
    const prevBtn = document.querySelector('.prev-btn');
    const nextBtn = document.querySelector('.next-btn');
    const indicators = document.querySelectorAll('.indicator');
    let currentSlide = 0;
    let slideInterval;

    // 初始化轮播图
    function initCarousel() {
        // 设置第一张幻灯片为活动状态
        slides[currentSlide].classList.add('active');
        indicators[currentSlide].classList.add('active');

        // 启动自动播放
        startAutoPlay();
    }

    // 切换到指定幻灯片
    function goToSlide(index) {
        // 移除当前活动状态
        slides[currentSlide].classList.remove('active');
        indicators[currentSlide].classList.remove('active');

        // 更新当前幻灯片索引
        currentSlide = index;

        // 添加新活动状态
        slides[currentSlide].classList.add('active');
        indicators[currentSlide].classList.add('active');
    }

    // 下一张幻灯片
    function nextSlide() {
        const nextIndex = (currentSlide + 1) % slides.length;
        goToSlide(nextIndex);
    }

    // 上一张幻灯片
    function prevSlide() {
        const prevIndex = (currentSlide - 1 + slides.length) % slides.length;
        goToSlide(prevIndex);
    }

    // 启动自动播放
    function startAutoPlay() {
        slideInterval = setInterval(nextSlide, 4000);
    }

    // 停止自动播放
    function stopAutoPlay() {
        clearInterval(slideInterval);
    }

    // 事件监听器
    prevBtn.addEventListener('click', function() {
        prevSlide();
        stopAutoPlay();
        startAutoPlay();
    });

    nextBtn.addEventListener('click', function() {
        nextSlide();
        stopAutoPlay();
        startAutoPlay();
    });

    // 指示器点击事件
    indicators.forEach(indicator => {
        indicator.addEventListener('click', function() {
            const slideIndex = parseInt(this.getAttribute('data-index'));
            goToSlide(slideIndex);
            stopAutoPlay();
            startAutoPlay();
        });
    });

    // 鼠标悬停时暂停自动播放
    const carouselContainer = document.querySelector('.carousel-container');
    carouselContainer.addEventListener('mouseenter', stopAutoPlay);
    carouselContainer.addEventListener('mouseleave', startAutoPlay);

    // 触摸设备支持
    let startX = 0;
    let endX = 0;

    carouselContainer.addEventListener('touchstart', function(e) {
        startX = e.touches[0].clientX;
    });

    carouselContainer.addEventListener('touchend', function(e) {
        endX = e.changedTouches[0].clientX;
        handleSwipe();
    });

    function handleSwipe() {
        const swipeThreshold = 50;
        const diff = startX - endX;

        if (Math.abs(diff) > swipeThreshold) {
            if (diff > 0) {
                // 向左滑动 - 下一张
                nextSlide();
            } else {
                // 向右滑动 - 上一张
                prevSlide();
            }
            stopAutoPlay();
            startAutoPlay();
        }
    }

    // 初始化轮播图
    initCarousel();
});
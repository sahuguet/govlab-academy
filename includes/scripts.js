$(document).ready(function() {

	// Smooth Scrolling Function.

	$(function() {
		$('a[href*=#]:not([href=#])').click(function() {
			if (location.pathname.replace(/^\//,'') == this.pathname.replace(/^\//,'')
				|| location.hostname == this.hostname) {

				var target = $(this.hash);

				target = target.length ? target : $('[name=' + this.hash.slice(1) +']');

				if (target.length) {
					$('html,body').animate({ scrollTop: target.offset().top }, 1000);

					return false;
				}
			}
		});
	});

	// Basic Collapse function

	$('.e-trigger').click(function() {
		$(this).toggleClass('m-active');
	});

	$('.e-trigger').click(function() {
		$('.b-top-layer').toggleClass('m-active');
	});
});


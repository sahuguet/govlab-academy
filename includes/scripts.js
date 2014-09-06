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

	// Testing IndexOf
		// $( ".b-library-item" ).each(function( index ) {
		
	// 	var title = $(this).children('h3').text();

	// 	var title_init = title.indexOf('\u201c');
	// 	var title_fin = title.indexOf('\u201d');

	// 	title_new = title.substring(title_init + 1, title_fin - 1);

	// 	title = $('.e-library-item-title').text(title_new);		
	// var a = $("#container").children();

		// console.log(a);

	// });
});
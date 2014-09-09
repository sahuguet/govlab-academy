var $container = $('#container'), filters = {};
function addContent(item) {
	/* item :=
	content_type: string
	description: string
	nice-tags: array of string
	tags: array of string (same as above, longer version)
	title: string
	url: string
	*/

	var actionMap = { 'video': 'Watch', 'document': 'Read', 'expert': 'Connect'};
	var gl_item = $(sprintf('<div class="b-library-item" data-type="%(type)s" data-topic="%(topic)s">\
 <h3>%(title)s</h3>\
<p>%(description)s</p>\
<div class="e-library-controls"><a class="e-library-action" href="%(url)s">%(action)s</a></div>\
</div>', { 'type': item['content_type'], 'topic': item['nice-tags'].join(' '), 'title': item['title'], 'description': item['description'], 'url': item['url'], 'action': actionMap[item['content_type']]}));
	$('#container').append(gl_item);
} // addContent()

function updateCount() {
  $('#item-count').html($container.data('isotope').$filteredAtoms.length + " item(s) selected.");
}

function processContent() {
	$container.isotope({
  itemSelector : '.b-library-item',
  layoutMode: 'fitRows'
  // masonry: {
  //   columnWidth: 80
  // }
	});
 updateCount(); 
// filter buttons
$('.filter a').click(function(){
  var $this = $(this);
  // don't proceed if already selected
  if ( $this.hasClass('selected') ) {
    return;
  }
  
  var $optionSet = $this.parents('.option-set');
  // change selected class
  $optionSet.find('.selected').removeClass('selected');
  $this.addClass('selected');
  
  // store filter value in object
  // i.e. filters.color = 'red'
  var group = $optionSet.attr('data-filter-group');
  filters[ group ] = $this.attr('data-filter-value');
  // convert object into array
  var isoFilters = [];
  for ( var prop in filters ) {
    isoFilters.push( filters[ prop ] )
  }
  var selector = isoFilters.join('');
  $container.isotope({ filter: selector });
  updateCount();
  return false;
});
};


$(function() {
		$.get( "library.json", function( data ) {
    var all_tags = {};
    $.each(data, function(index, value) {
      if (value.title.indexOf('\u201c') != -1) {
        var title_init = value.title.indexOf('\u201c');
        var title_fin = value.title.indexOf('\u201d');

        value.title = value.title.substring(title_init + 1, title_fin - 1);

        $.each(value['nice-tags'], function(i, v) { all_tags[v] = value['tags'][i]; });
        addContent(value);
      }
    });
		// We create the right filers.
		$.each(all_tags, function(k, v) {
			// console.log(k + " " + v);
			$('#filter-by-topic').append($(sprintf('<li><a class="e-filter" href="#filter-topic-%(topic)s" data-filter-value="[data-topic~=\'%(topic)s\']">%(topicName)s</a>', { 'topic': k, 'topicName': v })));
		});

		processContent();
		
	});

    //...
});
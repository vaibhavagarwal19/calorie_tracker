$(document).ready(function() {

    // ========== FOOD SEARCH ==========
    var foodSearchTimer;
    $('#food-search').on('input', function() {
        var query = $(this).val();
        clearTimeout(foodSearchTimer);
        if (query.length < 2) { $('#food-search-results').hide(); return; }
        $('#food-search-results').empty().append('<div class="searching">Searching...</div>').show();
        foodSearchTimer = setTimeout(function() {
            $.get('/api/foods/?search=' + encodeURIComponent(query), function(data) {
                var results = $('#food-search-results').empty();
                if (data.length === 0) {
                    results.append('<div class="no-results">No foods found</div>');
                } else {
                    data.forEach(function(food) {
                        results.append(
                            '<div class="search-item" data-id="' + food.id + '" data-calories="' + food.calories + '">' +
                                '<div class="item-name">' + food.name + '</div>' +
                                '<div class="item-detail">' + food.food_group + ' &middot; ' + food.calories + ' cal/' + (food.serving_description || 'serving') + '</div>' +
                            '</div>'
                        );
                    });
                }
                results.show();
            });
        }, 300);
    });

    // Select food from search results
    $(document).on('click', '#food-search-results .search-item', function() {
        var id = $(this).data('id');
        var cal = $(this).data('calories');
        var name = $(this).find('.item-name').text();
        var select = $('#food-select');
        select.empty().append('<option value="' + id + '" data-calories="' + cal + '" selected>' + name + ' (' + cal + ' cal)</option>');
        $('#food-search').val('');
        $('#food-search-results').hide();
        updateFoodCalories();
    });

    // Hide search dropdowns when clicking outside
    $(document).on('click', function(e) {
        if (!$(e.target).closest('.search-wrapper').length) {
            $('.search-results').hide();
        }
    });

    // Load foods when food group changes
    $('#food-group-select').on('change', function() {
        var group = $(this).val();
        if (!group) return;
        $.get('/api/foods/?food_group=' + encodeURIComponent(group), function(data) {
            var select = $('#food-select');
            select.empty().append('<option value="">-- Select Food --</option>');
            data.forEach(function(food) {
                select.append('<option value="' + food.id + '" data-calories="' + food.calories + '">' +
                    food.name + ' (' + food.calories + ' cal/' + (food.serving_description || 'serving') + ')</option>');
            });
        });
    });

    // Update calorie display when food/servings change
    function updateFoodCalories() {
        var cal = $('#food-select option:selected').data('calories') || 0;
        var servings = parseFloat($('#food-servings').val()) || 1;
        $('#food-calories-display').text((cal * servings).toFixed(1));
    }
    $('#food-select').on('change', updateFoodCalories);
    $('#food-servings').on('input', updateFoodCalories);

    // ========== ACTIVITY SEARCH ==========
    var activitySearchTimer;
    $('#activity-search').on('input', function() {
        var query = $(this).val();
        clearTimeout(activitySearchTimer);
        if (query.length < 2) { $('#activity-search-results').hide(); return; }
        $('#activity-search-results').empty().append('<div class="searching">Searching...</div>').show();
        activitySearchTimer = setTimeout(function() {
            $.get('/api/activities/?search=' + encodeURIComponent(query), function(data) {
                var results = $('#activity-search-results').empty();
                if (data.length === 0) {
                    results.append('<div class="no-results">No activities found</div>');
                } else {
                    data.forEach(function(act) {
                        results.append(
                            '<div class="search-item" data-id="' + act.id + '" data-met="' + act.met_value + '">' +
                                '<div class="item-name">' + act.specific_motion + '</div>' +
                                '<div class="item-detail">' + act.activity_name + ' &middot; MET: ' + act.met_value + '</div>' +
                            '</div>'
                        );
                    });
                }
                results.show();
            });
        }, 300);
    });

    // Select activity from search results
    $(document).on('click', '#activity-search-results .search-item', function() {
        var id = $(this).data('id');
        var met = $(this).data('met');
        var name = $(this).find('.item-name').text();
        var select = $('#activity-motion-select');
        select.empty().append('<option value="' + id + '" data-met="' + met + '" selected>' + name + ' (MET: ' + met + ')</option>');
        $('#activity-search').val('');
        $('#activity-search-results').hide();
        $('#met-value-display').text(met);
    });

    // Load activities when activity name changes
    $('#activity-name-select').on('change', function() {
        var name = $(this).val();
        if (!name) return;
        $.get('/api/activities/?search=' + encodeURIComponent(name), function(data) {
            var select = $('#activity-motion-select');
            select.empty().append('<option value="">-- Select Motion --</option>');
            data.forEach(function(act) {
                if (act.activity_name === name) {
                    select.append('<option value="' + act.id + '" data-met="' + act.met_value + '">' +
                        act.specific_motion + ' (MET: ' + act.met_value + ')</option>');
                }
            });
        });
    });

    // Update activity MET display
    $('#activity-motion-select, #activity-duration').on('change input', function() {
        var met = $('#activity-motion-select option:selected').data('met') || 0;
        $('#met-value-display').text(met);
    });

    // ========== SAVE ENTRIES ==========
    $('#save-food-btn').on('click', function() {
        var data = {
            user_id: $('#modal-user-id').val(),
            date: $('#food-date').val(),
            food_id: $('#food-select').val(),
            servings: $('#food-servings').val(),
            meal_type: $('#food-meal-type').val()
        };
        if (!data.food_id) { showToast('Please select a food item.', 'error'); return; }
        $.ajax({
            url: '/api/add-food-entry/',
            method: 'POST',
            contentType: 'application/json',
            data: JSON.stringify(data),
            headers: {'X-CSRFToken': getCookie('csrftoken')},
            success: function() {
                showToast('Food entry saved!', 'success');
                $('#addDataModal').modal('hide');
                setTimeout(function() { location.reload(); }, 1000);
            },
            error: function(xhr) { showToast('Error: ' + xhr.responseText, 'error'); }
        });
    });

    $('#save-activity-btn').on('click', function() {
        var data = {
            user_id: $('#modal-user-id').val(),
            date: $('#activity-date').val(),
            activity_id: $('#activity-motion-select').val(),
            duration_minutes: $('#activity-duration').val()
        };
        if (!data.activity_id) { showToast('Please select an activity.', 'error'); return; }
        $.ajax({
            url: '/api/add-activity-entry/',
            method: 'POST',
            contentType: 'application/json',
            data: JSON.stringify(data),
            headers: {'X-CSRFToken': getCookie('csrftoken')},
            success: function() {
                showToast('Activity entry saved!', 'success');
                $('#addDataModal').modal('hide');
                setTimeout(function() { location.reload(); }, 1000);
            },
            error: function(xhr) { showToast('Error: ' + xhr.responseText, 'error'); }
        });
    });

    // ========== UTILS ==========
    function getCookie(name) {
        var value = '; ' + document.cookie;
        var parts = value.split('; ' + name + '=');
        if (parts.length === 2) return parts.pop().split(';').shift();
    }
});

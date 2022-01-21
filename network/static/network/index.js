$(document).ready(() => {
	// Submit post on submit of new post form
	$('#newpost-form').submit(submitPost);

	// Hide new post form container div and conditional alerts inside of it
	$('#newpost-wrapper').hide();
	$('#post-success-alert').hide();
	$('#post-failed-alert').hide();
	$('.edit-form').toggle();

	// Toggle new post div visibility with slide animation
	$('#new-post').click(() => {
		$('#newpost-wrapper').slideToggle(300);
	});

	// Follow user upon clicking follow button
	const username = $('#username').text();
	$('#follow-btn').click(() => {
		follow(username);
	});

	// Handle like button click
	document.querySelectorAll('.like').forEach((element) => {
		const post_id = element.dataset.post_id;
		element.onclick = () => {
			like(post_id);
		};
	});

	// Show edit post form on edit button click
	document.querySelectorAll('.edit-btn').forEach((btn) => {
		btn.addEventListener('click', () => {
			const postId = btn.dataset.post_id;
			showEditForm(postId);
		});
	});

	// Handle edit form submit
	document.querySelectorAll('.edit-form').forEach((form) => {
		form.onsubmit = (event) => {
			event.preventDefault();
			console.log(event.target);
			const form = event.target;
			const formdata = new FormData(form);
			const postId = formdata.get('post-id');
			const postContent = formdata.get('content');
			submitEdit(postId, postContent);
		};
	});
});

// Submits post by making POST request to API
function submitPost(event) {
	// Prevent page refresh
	event.preventDefault();

	// Send POST request to API
	fetch('/new_post', {
		method: 'POST',
		headers: {
			'Content-Type': 'application/json',
		},
		body: JSON.stringify({
			content: $('#newpost-content').val(),
		}),
	})
		.then((response) => response.json())
		.then((result) => {
			if (result.status == 201) {
				$('#newpost-content').val('');
				$('#post-success-alert').slideDown();
				$('#post-failed-alert').slideUp();
			} else {
				console.log(result.error);
				throw new Error(result.error);
			}
		})
		.catch((error) => {
			$('#post-success-alert').slideUp();
			$('#post-failed-alert').slideDown();
			$('#post-failed-alert').text(`Post could not be submitted - ${error}`);
		});
}

// Sends POST request to like some user
function follow(username) {
	fetch(`/follow/${username}`)
		.then((response) => response.json())
		.then((result) => {
			if (result.status === 201) {
				updateFollowCount(username);
			} else {
				throw new Error(result.error);
			}
		})
		.catch((err) => {
			console.log(err);
		});
}

// Updates followers / following count on profile by making GET request
function updateFollowCount(username) {
	fetch(`/follow_count/${username}`)
		.then((response) => response.json())
		.then((result) => {
			$('#followers').text(result.follower_count);
			$('#following').text(result.following_count);
			const followBtnText = $('#follow-btn').text();
			$('#follow-btn').text(followBtnText === 'Follow' ? 'Unfollow' : 'Follow');
		});
}

// Sends POST request to like some post
function like(postId) {
	fetch(`/like/${postId}`)
		.then((response) => response.json())
		.then((result) => {
			if (result.status === 201) {
				updateLikeCount(postId);
			} else {
				throw new Error(result.error);
			}
		})
		.catch((err) => {
			console.log(err);
		});
}

// Updates like count on posts by making GET request
function updateLikeCount(postId) {
	fetch(`/like_count/${postId}`)
		.then((response) => response.json())
		.then((result) => {
			document.querySelectorAll('.like-count').forEach((likeCountElement) => {
				if (likeCountElement.dataset.post_id === postId) {
					likeCountElement.innerHTML = result.like_count;

					// Change icon styling (Filled / unfilled, heart and text color)
					const icon =
						likeCountElement.previousSibling.previousSibling;
					if (icon.className.includes('liked')) {
						icon.className = 'bi bi-heart me-2';
					} else {
						icon.className = 'bi bi-heart-fill me-2 liked';
					}
					likeCountElement.classList.toggle('liked');
				}
			});
		});
}

// Toggles between hiding / showing the form to edit posts
function showEditForm(postId) {
	const content = $(`#post-content-${postId}`);

	// console.log(content)
	content.slideToggle();
	$(`#edit-form-${postId}`).slideToggle();
	$(`#textarea-${postId}`).text(content.text());
	// console.log('Show Edit Form')
}

// Submits post edits by making PUT request to API
function submitEdit(postId, content) {
	fetch(`/edit_post/${postId}`, {
		method: 'PUT',
		headers: {
			'Content-Type': 'application/json',
		},
		body: JSON.stringify({
			content: content,
		}),
	})
		.then((response) => response.json())
		.then((result) => {
			$(`#post-content-${postId}`).text(result.new_content);
			showEditForm(postId);
		});
}

$(document).ready(function(){
	$("#footer1").hide();
	$("#footer2").hide();
});

$('#s1-next').click(function(){
	jQuery('#sform1').addClass('d-none');
	jQuery('#sform2').removeClass('d-none');
  });

$('#s2-prev').click(function(){
jQuery('#sform2').addClass('d-none');
jQuery('#sform1').removeClass('d-none');
	});

$('#s2-next').click(function(){
	jQuery('#sform2').addClass('d-none');
	jQuery('#sform3').removeClass('d-none');
	});

$('#s3-prev').click(function(){
	jQuery('#sform3').addClass('d-none');
	jQuery('#sform2').removeClass('d-none');
	});
	
$('#s3-next').click(function(event) {
	if (selectedArtists.length === 0) {
		event.preventDefault();
		submitButton.disabled = true;
		artistAlert.style.display = 'block';
	}
	});
	
let slideIndex = 1;
showSlides(slideIndex);

function plusSlides(n) {
  showSlides(slideIndex += n);
}

function currentSlide(n) {
  showSlides(slideIndex = n);
}

function showSlides(n) {
  let i;
  let slides = document.getElementsByClassName("mySlides");
  let dots = document.getElementsByClassName("dot");
  if (n > slides.length) {slideIndex = 1}    
  if (n < 1) {slideIndex = slides.length}
  for (i = 0; i < slides.length; i++) {
    slides[i].style.display = "none";  
  }
  for (i = 0; i < dots.length; i++) {
    dots[i].className = dots[i].className.replace(" dotactive", "");
  }
  slides[slideIndex-1].style.display = "block";  
  dots[slideIndex-1].className += " dotactive";
}

let selectedGenres = [];
let selectedArtists = [];
const submitButton = document.getElementById('s3-next');
const artistAlert = document.getElementById('artist-alert');


function addGenre(genre) {
	if (!selectedGenres.includes(genre) && selectedGenres.length < 5) {
	  selectedGenres.push(genre);
	  updateUIGenres();
	}
  }
  
  function removeGenre(genre) {
	selectedGenres = selectedGenres.filter(g => g !== genre);
	updateUIGenres();
  }
  
  function updateUIGenres() {
	const selectedGenresElement = document.getElementById('selected-genres');
	console.log('Yes');
	selectedGenresElement.innerHTML = '';
	selectedGenres.forEach(genre => {
	  const genreElement = document.createElement('div');
	  genreElement.textContent = genre;
	  genreElement.classList.add('selected-genre');
	  selectedGenresElement.appendChild(genreElement);
	});
  }

  function addArtist(event, artistId, artistName) {
    event.preventDefault();
    if (!selectedArtists.some(a => a.id === artistId)) {
      selectedArtists.push({ id: artistId, name: artistName });
      updateUI();
    }
  }

  function removeArtist(event, artistId) {
    event.preventDefault();
    selectedArtists = selectedArtists.filter(a => a.id !== artistId);
    updateUI();
  }

  function updateUI() {
      if (selectedArtists.length > 0) {
          submitButton.disabled = false;
          artistAlert.style.display = 'none';
      }

      const selectedArtistsElement = document.getElementById('selected-artists');
      selectedArtistsElement.innerHTML = '';
      const singerDict = {};
      selectedArtists.forEach(artist => {
          const artistElement = document.createElement('div');
          artistElement.classList.add('artist');
          artistElement.innerHTML = `
          <div style="display: flex; align-items: center; margin: 10px 0;
          border: 1px solid #181818;
          width: max-content;
          height: 3rem;
          border-radius: 25px;
          justify-content: center;
          text-align: center;
          padding: 0 10px;">
              <p style="color: #181818;">${artist.name}</p>
              <button class="remove" data-id="${artist.id}" onclick="removeArtist(event, '${artist.id}')">X</button>
          </div>
          `;
          selectedArtistsElement.appendChild(artistElement);
          singerDict[artist.name] = artist.id;
      });
      document.getElementById('singer-dict').value = JSON.stringify(singerDict);
  }
  

class CustomSelect {
	constructor(originalSelect) {
	  this.originalSelect = originalSelect;
	  this.customSelect = document.createElement("div");
	  this.customSelect.classList.add("select");
  
	  this.originalSelect.querySelectorAll("option").forEach((optionElement) => {
		const itemElement = document.createElement("div");
  
		itemElement.classList.add("select__item");
		itemElement.textContent = optionElement.textContent;
		this.customSelect.appendChild(itemElement);
  
		if (optionElement.selected) {
		  this._select(itemElement);
		}
  
		itemElement.addEventListener("click", () => {
			if (
				this.originalSelect.multiple &&
				itemElement.classList.contains("select__item--selected")
			  ) {
				this._deselect(itemElement);
				removeGenre(itemElement.textContent);
			  } else if (
				this.originalSelect.multiple &&
				selectedGenres.length < 5
			  ) {
				this._select(itemElement);
				addGenre(itemElement.textContent);
			  } else if (!this.originalSelect.multiple) {
				this._select(itemElement);
			  }
			console.log(selectedGenres);
		});
	  });
  
	  this.originalSelect.insertAdjacentElement("afterend", this.customSelect);
	  this.originalSelect.style.display = "none";
	}
  
	_select(itemElement) {
	  const index = Array.from(this.customSelect.children).indexOf(itemElement);
  
	  if (!this.originalSelect.multiple) {
		this.customSelect.querySelectorAll(".select__item").forEach((el) => {
		  el.classList.remove("select__item--selected");
		  $("#footer1").hide();
		  $("#footer2").hide();
		});
	  }
  
	  this.originalSelect.querySelectorAll("option")[index].selected = true;
	  itemElement.classList.add("select__item--selected");
	  $("#footer1").show();
	  $("#footer2").show();
	  console.log(selectedGenres);
	}
  
	_deselect(itemElement) {
	  const index = Array.from(this.customSelect.children).indexOf(itemElement);

	  this.originalSelect.querySelectorAll("option")[index].selected = false;
	  itemElement.classList.remove("select__item--selected");
	  $("#footer1").hide();
	  $("#footer2").hide();
	}
  }
  
  document.querySelectorAll(".custom-select").forEach((selectElement) => {
	new CustomSelect(selectElement);
  });

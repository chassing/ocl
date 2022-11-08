tapes = $(wildcard demo/*.tape)
gifs = $(tapes:%.tape=%.gif)

update-demos: $(gifs)

$(gifs): %.gif: %.tape
	cd demo && vhs < $(notdir $?)

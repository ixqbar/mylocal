/*
 ============================================================================
 Name        : RC4.c
 Author      : xingqiba
 Version     : 0.0.1
 Copyright   : copyright notice
 Description : Hello RC4 in C, Ansi-style
 ============================================================================
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "base64.h"

#define STATE_LEN 256

void ksa(unsigned char state[], unsigned char key[], int len) {
	int i, j = 0, t;

	for (i = 0; i < STATE_LEN; ++i) {
		state[i] = i;
	}

	for (i = 0; i < STATE_LEN; ++i) {
		j = (j + state[i] + key[i % len]) % STATE_LEN;
		t = state[i];
		state[i] = state[j];
		state[j] = t;
	}
}

void prga(unsigned char state[], unsigned char out[], int len) {
	int i = 0, j = 0, x, t;

	for (x = 0; x < len; ++x) {
		i = (i + 1) % STATE_LEN;
		j = (j + state[i]) % STATE_LEN;
		t = state[i];
		state[i] = state[j];
		state[j] = t;
		out[x] ^= state[(state[i] + state[j]) % STATE_LEN];
	}
}

int main(int argc, char *argv[]) {
	if (argc <= 1) {
		fprintf(stderr, "Please usage like %s ENCRYPT_TEXT\n\n", argv[0]);
		return 1;
	}

	int len = strlen(argv[1]);
	unsigned char *key;
	key = malloc(len);
	if (key == NULL) {
		fprintf(stderr, "malloc failed\n\n");
		return 1;
	}
	memcpy(key, argv[1], len);

	unsigned char state[STATE_LEN];
	unsigned char stream[] = "helloworld";

	printf("%s\n", stream);

	ksa(state, key, len);
	prga(state, stream, sizeof(stream) - 1);

	size_t out_len = 0;
	unsigned char * out = base64_encode(stream, sizeof(stream) - 1, &out_len);

	printf("%.*s\n", (int)out_len, out);

	free(out);
	free(key);

	return 0;
}

P = 0;
for (I = 1; I < 10; I = I + 1) {
	if (I % 2 == 1) P += I * 2 - 1;
	else P -= I * 2 - 1;
}
P;

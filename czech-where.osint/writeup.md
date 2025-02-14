# Czech Where? (Iris CTF 2024 - Open-Source Intelligence)

## Challenge
Iris visited this cool shop a while back, but forgot where it was! What street is it on?

### Resource
[Download czech-where.tar.gz](https://cdn.2024.irisc.tf/czech-where.tar.gz)

## Manual solve

Let's extract the czech-where.tar.gz file:

```bash
7z x ./resource/czech-where.tar.gz -o./resource/
```

```bash
7z x ./resource/czech-where.tar -o./resource/
```

Open image.png in ./resource/czech-where/

![czech-where-image.png](./images/czech-where-image.png)

We can see that the shop has "Czech wooden products" written on it. We search for it on Google Maps and the first result is:

![czech-where-maps-1.png](./images/czech-where-maps-1.png)

The shop in the result looks very similar to the image from the resource.

![czech-where-maps-2.png](./images/czech-where-maps-2.png)

Therefore, the location is Zlatá ulička u Daliborky, 119 00 Praha 1-Hradčany, Czechia and the street is Zlatá ulička u Daliborky.

Given that the challenge indicates the flag format:
> flag is all lowercase and _ for spaces. Please remove all accent marks if there are any. Wrap your answer in irisctf{}.

We can fix the format with the following Python script:

```py
import unicodedata

location_name = "Zlatá ulička u Daliborky"

# Convert to lowercase
location_name = location_name.lower()

# Replace whitespace with underscores
location_name = location_name.replace(" ", "_")

# Remove accent marks
location_name = ''.join(c for c in unicodedata.normalize('NFD', location_name) if unicodedata.category(c) != 'Mn')
print("[+] Flag: irisctf{{{}}}".format(location_name))
```

### Flag
Flag: `irisctf{zlata_ulicka_u_daliborky}`

![Solved](./images/czech-where-solved.png)

## Solution using solve.py

**NOTE**: since the script uses web scraping, it might stop working correctly if Google Maps gets updated. An alternative would be to create a script that uses an API Key.

Execute the following command:

```bash
python solve.py
```

It will show the flag in the output and write it to the flag.txt file in the relative ./solve directory

![Solved using python script](./images/czech-where-python-solve.png)
# Declare the variable
SOURCEURL='https://website.com/'  # substitute your source url

urlencode() {
    # urlencode <string>
    old_lc_collate=$LC_COLLATE
    LC_COLLATE=C

    local length="${#1}"
    for (( i = 0; i < length; i++ )); do
        local c="${1:i:1}"
        case $c in
            [a-zA-Z0-9.~_-]) printf "$c" ;;
            *) printf '%%%02X' "'$c" ;;
        esac
    done

    LC_COLLATE=$old_lc_collate
}

urldecode() {
    # urldecode <string>
    local url_encoded="${1//+/ }"
    printf '%b' "${url_encoded//%/\\x}"
}

readarray -t list < doilist.txt

for doi in "${list[@]}"
do
    echo "Download article with doi: $doi"
    response=$(curl -s -L "$SOURCEURL" --compressed \
        -H "User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:75.0) Gecko/20100101 Firefox/75.0" \
        -H "Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8" \
        -H "Accept-Language: en-US,en;q=0.5" \
        -H "Content-Type: application/x-www-form-urlencoded" \
        -H "Origin: $SOURCEURL" \
        -H "DNT: 1" \
        -H "Connection: keep-alive" \
        -H "Referer: $SOURCEURL" \
        -H "Cookie: __ddg1=SFEVzNPdQpdmIWBwzsBq; session=45c4aaad919298b2eb754b6dd84ceb2d; refresh=1588795770.5886; __ddg2=your_generic_value" \
        -H "Upgrade-Insecure-Requests: 1" \
        -H "Pragma: no-cache" \
        -H "Cache-Control: no-cache" \
        -H "TE: Trailers" \
        --data "request=$(urlencode $doi)" \
        -D -)

    pdf_url=$(echo "$response" \
        | pup 'embed#pdf attr{src}' \
        | sed -e 's/&amp;/\&/g' -e 's|^//|https://|' -e 's|#.*$||')


    filename=$(basename "$pdf_url")
    doi_code="${doi#*doi.org/}"
    echo "doi_code: $doi_code"
    doi_decoded=$(urldecode "$doi_code")
    doi_decoded="${doi_decoded//\//_}"  # Replace forward slashes with underscores
    output_filename="${filename%.pdf}_${doi_decoded}.pdf"
    echo "output_filename: $output_filename"
    echo "Found link: $pdf_url"

    curl -s -L $pdf_url --output $output_filename
    #echo "Response: $response"
done

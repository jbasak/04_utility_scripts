# Edureka PDF Download Guide

This guide explains how to download a presentation PDF from an Edureka classroom page that you can already access with your own account.

The downloader does not log in, bypass access controls, or guess protected API endpoints. It uses your authenticated browser cookies and, when necessary, a PDF URL obtained from the browser's Network tools.

## Location

The program is:

```text
04_utility_scripts/download_edureka_pdf.py
```

The input configuration file is:

```text
04_utility_scripts/edureka_download_config.ini
```

The default output file is:

```text
04_utility_scripts/edureka_presentation.pdf
```

## 1. Sign in to Edureka

1. Open Chrome or Edge.
2. Sign in to Edureka normally.
3. Open the classroom presentation URL, for example:

```text
https://learning.edureka.co/classroom/presentation/3103/35187/2575280?tab=CourseContent
```

4. Confirm that the presentation is available in the browser.

## 2. Export the browser cookies

The script needs an authenticated cookie file in Netscape format.

1. Install a trusted browser cookie-export extension that supports Netscape format, such as `Get cookies.txt LOCALLY`.
2. Keep the Edureka classroom page open and signed in.
3. Use the extension on the Edureka page.
4. Export the cookies for the current site.
5. Save the exported file as:

```text
C:\BASAK\Codebase\github_repos\04_utility_scripts\edureka-cookies.txt
```

The file should begin with a Netscape cookie header or contain tab-separated cookie records. Do not edit or paste the cookie values into source code.

## 3. Configure the download

Edit `edureka_download_config.ini` instead of editing the Python program:

```ini
[download]
page_url = https://learning.edureka.co/classroom/presentation/3103/35187/2575280?tab=CourseContent
pdf_url =
cookie_file = edureka-cookies.txt
output_file = edureka_presentation.pdf
timeout_seconds = 30
```

Normally, leave `pdf_url` empty. The script will first look for a PDF link in the classroom page HTML.

## 4. Run the program

From PowerShell:

```powershell
cd C:\BASAK\Codebase\github_repos\04_utility_scripts
python .\download_edureka_pdf.py
```

The downloaded file will be written to the path configured by `output_file`.

## 5. If no PDF URL is found

Edureka may load the presentation URL dynamically with JavaScript. In that case, the initial HTML does not contain the actual PDF URL.

### Alternatives to F12

On Windows, use any of these methods to open browser developer tools:

- Chrome or Edge: press `Ctrl+Shift+I`.
- Right-click the classroom page and select **Inspect**.
- Open the browser menu, then choose **More tools > Developer tools**.
- On some keyboards, use `Fn+F12` if the function keys are assigned to media controls.

If developer tools are disabled by a company or school policy, use Edureka's official download control directly. If no official download is available, contact Edureka support or use the browser's permitted document-viewer save option. Do not try to bypass the restriction.

Once developer tools are open, use the browser's Network tools:

1. Open the classroom page while signed in.
2. Open the **Network** tab.
3. Enable **Preserve log**.
4. Filter requests using `pdf`.
5. Use Edureka's official presentation or download control.
6. Find the request that returns the PDF.
7. Right-click it and choose **Copy > Copy URL**.
8. Set the copied URL in `edureka_download_config.ini`:

```ini
pdf_url = https://example-cdn.example/presentation.pdf
```

Then run the program again:

```powershell
python .\download_edureka_pdf.py
```

Alternatively, pass the URL without editing the file:

```powershell
python .\download_edureka_pdf.py --pdf-url "https://example-cdn.example/presentation.pdf"
```

The direct URL may be temporary and may need to be copied again later.

## 6. Optional command-line parameters

The command-line options override the values in the configuration file:

```powershell
python .\download_edureka_pdf.py `
  --pdf-url "https://example-cdn.example/presentation.pdf" `
  --cookie-file "C:\path\to\edureka-cookies.txt" `
  --output "C:\path\to\presentation.pdf" `
  --timeout 60
```

The available options are:

```text
url                  Authenticated classroom page URL
--pdf-url            Direct PDF URL from the browser Network tab
-c, --cookie-file    Netscape browser cookie export
-o, --output         Destination PDF path
--timeout            Network timeout in seconds
```

## Troubleshooting

### Cookie file not found

Check that this file exists:

```text
C:\BASAK\Codebase\github_repos\04_utility_scripts\edureka-cookies.txt
```

You can also provide another path with `--cookie-file` or update `cookie_file` in `edureka_download_config.ini`.

### Invalid cookie file

Export the cookies again in Netscape format. A JSON cookie export is not accepted by this program.

### No PDF URL was found in the page HTML

Use the Network-tab procedure above and provide the direct URL with `pdf_url` or `--pdf-url`.

### Candidate did not return a PDF

The URL may have expired, may require a fresh authenticated session, or may return an HTML login page instead of a PDF. Sign in again, export fresh cookies, and copy a new PDF request URL.

## Security and usage notes

- Treat `edureka-cookies.txt` like a password.
- Never commit, email, upload, or share the cookie file.
- Do not place cookie values, passwords, or tokens in Python source code.
- Delete the cookie file after use if it is no longer needed.
- Use the program only for content you are authorized to access and download.
- Follow Edureka's terms, copyright rules, and download permissions.

# List of all Edureka GenAI PDP URLS to download presentation.

## URLS for Python course modules
### https://s3.amazonaws.com/module-non-videos/3098_m1_presentation_v1_2nd_lcykxs8.pdf
### https://s3.amazonaws.com/module-non-videos/3098_m2_presentation_v1_92p_s1lqkgq.pdf
### https://s3.amazonaws.com/module-non-videos/3098_m3_p1_presentation_v1_0wt_1lwap8cj.pdf
### https://s3.amazonaws.com/module-non-videos/3098_m3_p2_presentation_v1_ra2_ua6h7jpg.pdf
### #https://s3.amazonaws.com/module-non-videos/3098_m4_p1_presentation_v1_bli_syii6ehk.pdf
### #https://s3.amazonaws.com/module-non-videos/3098_m4_p2_presentation_v1_0b8_pwqmnq8.pdf

## URLs for Machine Learning course modules
### https://s3.amazonaws.com/module-non-videos/3033_module1_presentation_v1_9ty_6j45zvp.pdf
### https://s3.amazonaws.com/module-non-videos/3033_module2_presentation_v1_xey_injq7mtf.pdf
### https://s3.amazonaws.com/module-non-videos/3033_module3_presentation_v1_3wi_2x0r00z.pdf
### https://s3.amazonaws.com/module-non-videos/3033_module4_presentation_v1_d43_e5cb2qj.pdf
### https://s3.amazonaws.com/module-non-videos/3033_module_5_presentation_v1_yom_osoc3py.pdf
### https://s3.amazonaws.com/module-non-videos/3033_module6_presentation_v1_kfj_2ofirt2.pdf
### https://s3.amazonaws.com/module-non-videos/3033_module_7_presentation_v1_ez3_rzixbzx.pdf
### https://s3.amazonaws.com/module-non-videos/3033_module8_presentation_v1_32n_k0xic8m.pdf

##  URLs for Deep Learning course modules
### https://s3.amazonaws.com/module-non-videos/3034_module1_presentation_v1_2y8_kj4zwqs.pdf
### https://s3.amazonaws.com/module-non-videos/3034_module2_presentation_v1_kco_yvozhvp.pdf
### https://s3.amazonaws.com/module-non-videos/3034_module3_presentation_v1_j3b_b1zeilq.pdf
### https://s3.amazonaws.com/module-non-videos/3034_module4_presentation_v1_44d_d9talt2.pdf
### https://s3.amazonaws.com/module-non-videos/3034_module5_presentation_v1_9w3_emskw8d.pdf
### https://s3.amazonaws.com/module-non-videos/3034_module6_presentation_v1_yu6_gcaexbq.pdf


## URLS for Natural Language Processing course modules
### https://s3.amazonaws.com/module-non-videos/3035_module1_presentation_v1_riq_nvtiv7d.pdf
### https://s3.amazonaws.com/module-non-videos/3035_module2_presentation_v1_fx0_z6o94au.pdf
### https://s3.amazonaws.com/module-non-videos/3035_module3_presentation_v1_plb_nslnhob.pdf
### https://s3.amazonaws.com/module-non-videos/3035_module4_presentation_v1_exy_kw9sh5n.pdf
### https://s3.amazonaws.com/module-non-videos/3035_module5_presentation_v1_xop_thia0ou.pdf
### https://s3.amazonaws.com/module-non-videos/3035_module6_presentation_v1_q4h_6puj8lrh.pdf
### https://s3.amazonaws.com/module-non-videos/3035_module7_presentation_v1_eh7_1ucqaxu.pdf
### https://s3.amazonaws.com/module-non-videos/3035_module8_presentation_v1_v95_i6y49b2.pdf
### https://s3.amazonaws.com/module-non-videos/3035_module9_presentation_v1_fr8_dwwpu54k.pdf
### https://s3.amazonaws.com/module-non-videos/3035_module10_presentation_v1_arz_oec4byy.pdf


## URLs for Generative AI course modules
### https://s3.amazonaws.com/module-non-videos/3036_module1_presentation_v1_wwt_u3sv6sr.pdf
### https://s3.amazonaws.com/module-non-videos/3036_module2_presentation_v1_7qx_smoogaf.pdf
### https://s3.amazonaws.com/module-non-videos/3036_module3_presentation_v1_xpi_00syeuu.pdf
### https://s3.amazonaws.com/module-non-videos/3036_module04_presentation_v1_xei_lbaqcu1.pdf
### https://s3.amazonaws.com/module-non-videos/3036_module5_presentation_v1_ja7_26jhgfq.pdf
### https://s3.amazonaws.com/module-non-videos/3036_module6_presentation_v1_89c_7isklhz.pdf

## URLs for LLM Power applicaiton development course modules
### https://s3.amazonaws.com/module-non-videos/3037_module1_presentation_v1_y6n_zddjfxw.pdf
### https://s3.amazonaws.com/module-non-videos/3037_module2_presentation_v1_ksl_urm5j4j.pdf
### #https://s3.amazonaws.com/module-non-videos/3037_module3_presentation_v1_gnb_jacdm77.pdf
### https://s3.amazonaws.com/module-non-videos/3037_module4_presentation_v1_8eg_oox82wi.pdf
### https://s3.amazonaws.com/module-non-videos/3037_module5_presentation_v1_87l_i6d2s16.pdf
### https://s3.amazonaws.com/module-non-videos/3037_module6_presentation_v1_n0q_41awif6.pdf
### https://s3.amazonaws.com/module-non-videos/3037_module7_presentation_v1_pqw_oz7uvl1j.pdf
### https://s3.amazonaws.com/module-non-videos/3037_module8_presentation_v1_ij0_pylwpg.pdf
### https://s3.amazonaws.com/module-non-videos/3037_module9_presentation_v1_oa0_kji3ggx.pdf

## URLS for Agentic AI course modules
### https://s3.amazonaws.com/module-non-videos/3038_module1_presentation_v1_qid_nllddjh.pdf
### #https://s3.amazonaws.com/module-non-videos/3038_module2_presentation_v1_mnn_qwr031n.pdf
### #https://s3.amazonaws.com/module-non-videos/3038_module3_presentation_v1_lmu_qn3wvc1h.pdf
### https://s3.amazonaws.com/module-non-videos/3038_module4_presentation_v1_1zz_dvi5qy.pdf
### https://s3.amazonaws.com/module-non-videos/3038_module5_presentation_v1_jou_hb238u3.pdf
### https://s3.amazonaws.com/module-non-videos/3038_module6_presentation_v1_ldz_qntc3ch.pdf
### https://s3.amazonaws.com/module-non-videos/3038_module7_presentation_v1_cdz_4ijow85.pdf
### https://s3.amazonaws.com/module-non-videos/3038_module8_presentation_v1_36q_h3burkz.pdf
### https://s3.amazonaws.com/module-non-videos/3038_module9_presentation_v1_g1n_s89ihey.pdf
### #https://s3.amazonaws.com/module-non-videos/3038_module10_presentation_v1_321_gfow0kxg.pdf

## URLS for Agentic AI Driven Sofware Engineering course modules
### https://s3.amazonaws.com/module-non-videos/3039_module1_presentation_v1_rlc_j2q712r.pdf
### https://s3.amazonaws.com/module-non-videos/3039_module2_presentation_v1_0q8_ncfdjcnh.pdf
### https://s3.amazonaws.com/module-non-videos/3039_module3_presentation_v1_31z_z9ll7lkl.pdf
### https://s3.amazonaws.com/module-non-videos/3039_module4_presentation_v1_owq_xsbs41t.pdf

## URLs for LLM Ops
### https://s3.amazonaws.com/module-non-videos/3040_module1_presentation_v1_1gj_h9d3jh4.pdf
### https://s3.amazonaws.com/module-non-videos/3040_module2_presentation_v1_uz0_strk0yb.pdf
### https://s3.amazonaws.com/module-non-videos/3040_module3_presentation_v1_p4t_zjbubm1.pdf
### https://s3.amazonaws.com/module-non-videos/3040_module4_presentation_v1_we1_weh5r5g.pdf
### https://s3.amazonaws.com/module-non-videos/3040_module5_presentation_v1_k3a_qzwwxzz.pdf
### https://s3.amazonaws.com/module-non-videos/3040_module6_presentation_v1_cbc_jwg8i6pf.pdf

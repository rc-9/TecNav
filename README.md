[![Issues][issues-shield]][issues-url]

[![alt_text](https://user-images.githubusercontent.com/79323360/170838284-edba9418-8f2b-4ca1-a880-db3651fbe247.png)](https://user-images.githubusercontent.com/79323360/170838284-edba9418-8f2b-4ca1-a880-db3651fbe247.png)
<br />
<!---
<div align="center">
  <a href="https://github.com/rc-9/TecNav">
    <img src=".png" alt="Logo" width="80" height="45">
  </a>
-->



<h1 align="center">TecNav</h1>
<h3 align="center">Clinic-Monitoring & Technician-Navigation Application</h3>
  <p align="center">
    University of Denver - Data Science Capstone
    <br />
    Tomer Danon & Romith Challa
    <br />
    <br />
    <a href="https://github.com/rc-9/TecNav">View Repo</a>
    ·
    <a href="https://github.com/rc-9/TecNav/issues">Report Bug</a>
    ·
    <a href="https://github.com/rc-9/TecNav/issues">Request Feature</a>
  </p>
</div>



<!-- TABLE OF CONTENTS -->
<details>
  <summary>Table of Contents</summary>
  <ol>
    <li>
      <a href="#about-the-project">About The Project</a>
    <li><a href="#usage">Usage</a></li>
    <li><a href="#contact">Contact</a></li>
    <li><a href="#acknowledgments">Acknowledgments</a></li>
  </ol>
</details>



## About The Project

According to a 2019 benchmark report from the Urgent Care Association, the number of urgent-care clinics increased by 9.6% from the previous year. 
As the pandemic continues to put a strain on the healthcare system, the appeal for convenient and affordable care-outlets is greater than ever. 
To meet this growing need for on-demand care, urgent-care clinics have been rapidly expanding the scope of their services to provide patients with a quick and affordable alternative to the emergency room. 
This proves to be a mutually exclusive endeavor as minimizing wait-times entails maximizing staff availability. 
Consequently, this leads to higher operational costs that eventually trickle down to patient bills. 
Due to the inconsistency in patient traffic, it is difficult to schedule staff to be able to handle the peak hours, without inevitably wasting resources during less busy hours. 
Some chain-operated clinics creatively handle this by transferring technicians between their various locations to account for the constantly evolving needs at each clinic. 
This requires continuous monitoring of each clinic to manually make navigation decisions based on the fluctuating patient traffic. 
Instead, a software application that streamlines this process to make real-time, data-driven navigation decisions would serve as an invaluable tool for these clinics. 
That is the motivation behind TecNav—an automated application that employs machine-learning to forecast the dynamic patient flow and navigate technicians without any human supervision. 
Based on the preliminary results of the prototype, TecNav can save clients over $90,000 for each clinic per year. 
This could potentially finance their mission to expand clinical services, without burdening patients with higher costs. 
Designed with an emphasis on translatability, TecNav’s algorithm is customizable to fit the needs of any potential client.

<p align="right">(<a href="#top">back to top</a>)</p>



## Usage

This section outlines the order to execute notebooks to generate, explore, model the data, and build the software navigation application.
<br/> <br/>

1. ```uc_data_fabricator.ipynb```: As there are no publicly-available datasets that fit the scope of this project, this notebook will execute a series of research-supported fabrication steps to generate datasets that emulate the real-world as much as possible. 
**NOTE: This step is optional and can be skipped as the ```fabricated_data``` folder contains pre-generated datasets that will be used in the notebooks below.**
<br/> <br/>

2. ```uc_eda.ipynb```: This notebook will explore the generated datasets to draw insights from the patient visits and any relationships between date/times to inform the modeling and navigation process. 
**NOTE: Not all visual outputs are pre-loaded. For best visual output and to utilize the interactive toggle-menu for plots, execute this script in a Jupyter notebook (VS-Code does not fully support .ipynb interactive widgets).**
<br/> <br/>

3. ```uc_modeler.ipynb```: This notebook will construct and evaluate baseline models to help select a decision-maker within the navigation software.
<br/> <br/>

4. ```uc_analysis.ipynb```: This notebook will implement technician-navigation to study the potential benefits in productivity and operational costs. 
This notebook utilizes ```uc_navigator.py``` and ```TecNav_Demo.py```.
<br/> <br/>

5. ```uc_navigator.py```: (FOR REFERENCE ONLY) Contains navigator application. This module is launched within ```uc_analysis.ipynb``` and ```TecNav_Demo.py```.
<br/> <br/>

6. ```TecNav_Demo.py```: (FOR REFERENCE ONLY) Contains demo dashboard application. This module is launched within ```uc_analysis.ipynb```.

<p align="right">(<a href="#top">back to top</a>)</p>



<!-- CONTACT -->
## Contact

* Tomer Danon - [tomer.danon@du.edu](tomer.danon@du.edu)
* Romith Challa - [romith.challa@du.edu](romith.challa@du.edu)

<p align="right">(<a href="#top">back to top</a>)</p>


## Acknowledgments

Data Science Capstone | Ritchie School of Engineering & Computer Science | University of Denver

<p align="right">(<a href="#top">back to top</a>)</p>



<!-- MARKDOWN LINKS & IMAGES -->
[issues-shield]: https://img.shields.io/github/issues/rc-9/TecNav.svg?style=for-the-badge
[issues-url]: https://github.com/rc-9/TecNav/issues


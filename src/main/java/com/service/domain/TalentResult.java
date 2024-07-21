package com.service.domain;

public class TalentResult {

    private String jobId;
    private String ksa;
    private String firstName;
    private String lastName;
    private String corporateTitle;
    private String location;
    private double score;
    private String serialNum;
    private String division;
    private String codeDescription;

    public void setCodeDescription(String codeDescription) {
        this.codeDescription = codeDescription;
    }
    public String getCodeDescription() {
        return codeDescription;
    }

    public void setDivision(String division) {
        this.division = division;
    }
    public String getDivision() {
        return division;
    }

    public void setSerialNum(String serialNum) {
        this.serialNum = serialNum;
    }
    public String getSerialNum() {
        return serialNum;
    }
    public void setKsa(String ksa) {
        this.ksa = ksa;
    }
    public String getKsa() {
        return ksa;
    }
    public void setScore(double score) {
        this.score = score;
    }
    public double getScore() {
        return score;
    }


    public void setCorporateTitle(String corporateTitle) {
        this.corporateTitle = corporateTitle;
    }
    public String getCorporateTitle() {
        return corporateTitle;
    }

    public void setLocation(String location) {
        this.location = location;
    }
    public String getLocation() {
        return location;
    }

    public void setJobId(String jobId) {
        this.jobId = jobId;
    }
    public String getJobId() {
        return jobId;
    }

    public void setFirstName(String firstName) {
        this.firstName = firstName;
    }
    public String getFirstName() {
        return firstName;
    }

    public void setLastName(String lastName) {
        this.lastName = lastName;
    }
    public String getLastName() {
        return lastName;
    }

}
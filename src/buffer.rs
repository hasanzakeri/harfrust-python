use harfrust::UnicodeBuffer;
use pyo3::exceptions::PyValueError;
use pyo3::prelude::*;

use crate::types::{PyDirection, PyLanguage, PyScript};

#[pyclass(name = "Buffer", unsendable)]
pub struct PyBuffer {
    pub(crate) inner: Option<UnicodeBuffer>,
}

impl PyBuffer {
    fn consumed_err() -> PyErr {
        PyValueError::new_err("Buffer has been consumed by shape()")
    }

    fn as_ref_buf(&self) -> PyResult<&UnicodeBuffer> {
        self.inner.as_ref().ok_or_else(Self::consumed_err)
    }

    fn as_mut_buf(&mut self) -> PyResult<&mut UnicodeBuffer> {
        self.inner.as_mut().ok_or_else(Self::consumed_err)
    }

    #[allow(dead_code)]
    pub(crate) fn take_inner(&mut self) -> PyResult<UnicodeBuffer> {
        self.inner.take().ok_or_else(Self::consumed_err)
    }

    #[allow(dead_code)]
    pub(crate) fn restore(&mut self, buf: UnicodeBuffer) {
        self.inner = Some(buf);
    }
}

#[pymethods]
impl PyBuffer {
    #[new]
    fn new() -> Self {
        PyBuffer {
            inner: Some(UnicodeBuffer::new()),
        }
    }

    fn __len__(&self) -> PyResult<usize> {
        Ok(self.as_ref_buf()?.len())
    }

    fn add_str(&mut self, s: &str) -> PyResult<()> {
        self.as_mut_buf()?.push_str(s);
        Ok(())
    }

    #[pyo3(signature = (codepoint, cluster=0))]
    fn add(&mut self, codepoint: u32, cluster: u32) -> PyResult<()> {
        let ch = char::from_u32(codepoint).ok_or_else(|| {
            PyValueError::new_err(format!("invalid unicode codepoint: U+{codepoint:04X}"))
        })?;
        self.as_mut_buf()?.add(ch, cluster);
        Ok(())
    }

    fn clear(&mut self) -> PyResult<()> {
        self.as_mut_buf()?.clear();
        Ok(())
    }

    fn reset_clusters(&mut self) -> PyResult<()> {
        self.as_mut_buf()?.reset_clusters();
        Ok(())
    }

    fn guess_segment_properties(&mut self) -> PyResult<()> {
        self.as_mut_buf()?.guess_segment_properties();
        Ok(())
    }

    fn reserve(&mut self, size: usize) -> PyResult<bool> {
        Ok(self.as_mut_buf()?.reserve(size))
    }

    fn set_pre_context(&mut self, s: &str) -> PyResult<()> {
        self.as_mut_buf()?.set_pre_context(s);
        Ok(())
    }

    fn set_post_context(&mut self, s: &str) -> PyResult<()> {
        self.as_mut_buf()?.set_post_context(s);
        Ok(())
    }

    fn set_not_found_variation_selector_glyph(&mut self, glyph: u32) -> PyResult<()> {
        self.as_mut_buf()?
            .set_not_found_variation_selector_glyph(glyph);
        Ok(())
    }

    #[getter]
    fn direction(&self) -> PyResult<PyDirection> {
        Ok(PyDirection(self.as_ref_buf()?.direction()))
    }

    #[setter]
    fn set_direction(&mut self, d: PyDirection) -> PyResult<()> {
        self.as_mut_buf()?.set_direction(d.0);
        Ok(())
    }

    #[getter]
    fn script(&self) -> PyResult<PyScript> {
        Ok(PyScript(self.as_ref_buf()?.script()))
    }

    #[setter]
    fn set_script(&mut self, s: PyScript) -> PyResult<()> {
        self.as_mut_buf()?.set_script(s.0);
        Ok(())
    }

    #[getter]
    fn language(&self) -> PyResult<Option<PyLanguage>> {
        Ok(self.as_ref_buf()?.language().map(PyLanguage))
    }

    #[setter]
    fn set_language(&mut self, l: PyLanguage) -> PyResult<()> {
        self.as_mut_buf()?.set_language(l.0);
        Ok(())
    }

    fn __repr__(&self) -> PyResult<String> {
        let buf = self.as_ref_buf()?;
        // NOTE: duplicated from PyDirection::__repr__ in types.rs (private there).
        // If Direction's repr labels ever change, update both sites — or promote
        // this match to a shared helper.
        let dir = match buf.direction() {
            harfrust::Direction::LeftToRight => "Direction.LTR",
            harfrust::Direction::RightToLeft => "Direction.RTL",
            harfrust::Direction::TopToBottom => "Direction.TTB",
            harfrust::Direction::BottomToTop => "Direction.BTT",
            harfrust::Direction::Invalid => "Direction(<invalid>)",
        };
        let script = buf.script().tag().to_string();
        let lang = buf
            .language()
            .map(|l| format!("\"{}\"", l.as_str()))
            .unwrap_or_else(|| "None".to_string());
        Ok(format!(
            "Buffer(len={}, direction={}, script=\"{}\", language={})",
            buf.len(),
            dir,
            script,
            lang,
        ))
    }
}

pub fn register(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_class::<PyBuffer>()?;
    Ok(())
}

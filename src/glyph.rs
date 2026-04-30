use harfrust::{GlyphBuffer, GlyphInfo, GlyphPosition, SerializeFlags};
use pyo3::exceptions::{PyIndexError, PyValueError};
use pyo3::prelude::*;

use crate::buffer::PyBuffer;
use crate::font::PyFont;

// ---------------------------------------------------------------------------
// GlyphInfo
// ---------------------------------------------------------------------------

#[pyclass(name = "GlyphInfo", frozen, from_py_object)]
#[derive(Clone, Copy)]
pub struct PyGlyphInfo {
    #[pyo3(get)]
    glyph_id: u32,
    #[pyo3(get)]
    cluster: u32,
    #[pyo3(get)]
    unsafe_to_break: bool,
    #[pyo3(get)]
    unsafe_to_concat: bool,
    #[pyo3(get)]
    safe_to_insert_tatweel: bool,
}

impl PyGlyphInfo {
    fn from_info(info: &GlyphInfo) -> Self {
        Self {
            glyph_id: info.glyph_id,
            cluster: info.cluster,
            unsafe_to_break: info.unsafe_to_break(),
            unsafe_to_concat: info.unsafe_to_concat(),
            safe_to_insert_tatweel: info.safe_to_insert_tatweel(),
        }
    }
}

#[pymethods]
impl PyGlyphInfo {
    fn __repr__(&self) -> String {
        format!(
            "GlyphInfo(glyph_id={}, cluster={})",
            self.glyph_id, self.cluster
        )
    }
}

// ---------------------------------------------------------------------------
// GlyphPosition
// ---------------------------------------------------------------------------

#[pyclass(name = "GlyphPosition", frozen, from_py_object)]
#[derive(Clone, Copy)]
pub struct PyGlyphPosition {
    #[pyo3(get)]
    x_advance: i32,
    #[pyo3(get)]
    y_advance: i32,
    #[pyo3(get)]
    x_offset: i32,
    #[pyo3(get)]
    y_offset: i32,
}

impl PyGlyphPosition {
    fn from_pos(pos: &GlyphPosition) -> Self {
        Self {
            x_advance: pos.x_advance,
            y_advance: pos.y_advance,
            x_offset: pos.x_offset,
            y_offset: pos.y_offset,
        }
    }
}

#[pymethods]
impl PyGlyphPosition {
    fn __repr__(&self) -> String {
        format!(
            "GlyphPosition(x_advance={}, y_advance={}, x_offset={}, y_offset={})",
            self.x_advance, self.y_advance, self.x_offset, self.y_offset
        )
    }
}

// ---------------------------------------------------------------------------
// GlyphBuffer
// ---------------------------------------------------------------------------

#[pyclass(name = "GlyphBuffer", unsendable)]
pub struct PyGlyphBuffer {
    inner: Option<GlyphBuffer>,
}

impl PyGlyphBuffer {
    pub(crate) fn wrap(buf: GlyphBuffer) -> Self {
        Self { inner: Some(buf) }
    }

    fn consumed_err() -> PyErr {
        PyValueError::new_err("GlyphBuffer has been consumed by clear()")
    }

    fn as_ref_buf(&self) -> PyResult<&GlyphBuffer> {
        self.inner.as_ref().ok_or_else(Self::consumed_err)
    }
}

#[pymethods]
impl PyGlyphBuffer {
    fn __len__(&self) -> PyResult<usize> {
        Ok(self.as_ref_buf()?.len())
    }

    #[getter]
    fn glyph_infos(&self) -> PyResult<Vec<PyGlyphInfo>> {
        Ok(self
            .as_ref_buf()?
            .glyph_infos()
            .iter()
            .map(PyGlyphInfo::from_info)
            .collect())
    }

    #[getter]
    fn glyph_positions(&self) -> PyResult<Vec<PyGlyphPosition>> {
        Ok(self
            .as_ref_buf()?
            .glyph_positions()
            .iter()
            .map(PyGlyphPosition::from_pos)
            .collect())
    }

    // Implementing __getitem__ + __len__ makes the buffer iterable in Python
    // via the legacy iteration protocol, so `for info, pos in gbuf:` works
    // without a separate iterator class.
    fn __getitem__(&self, index: isize) -> PyResult<(PyGlyphInfo, PyGlyphPosition)> {
        let buf = self.as_ref_buf()?;
        let len = buf.len() as isize;
        let idx = if index < 0 { index + len } else { index };
        if idx < 0 || idx >= len {
            return Err(PyIndexError::new_err("glyph index out of range"));
        }
        let i = idx as usize;
        Ok((
            PyGlyphInfo::from_info(&buf.glyph_infos()[i]),
            PyGlyphPosition::from_pos(&buf.glyph_positions()[i]),
        ))
    }

    fn clear(&mut self) -> PyResult<PyBuffer> {
        let inner = self.inner.take().ok_or_else(Self::consumed_err)?;
        Ok(PyBuffer {
            inner: Some(inner.clear()),
        })
    }

    fn serialize(&self, font: PyRef<'_, PyFont>) -> PyResult<String> {
        let buf = self.as_ref_buf()?;
        let font_ref = font.font_ref()?;
        let shaper = font.build_shaper(&font_ref);
        Ok(buf.serialize(&shaper, SerializeFlags::default()))
    }

    fn __repr__(&self) -> String {
        match self.inner.as_ref() {
            Some(b) => format!("GlyphBuffer(len={})", b.len()),
            None => "GlyphBuffer(<consumed>)".to_string(),
        }
    }
}

pub fn register(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_class::<PyGlyphInfo>()?;
    m.add_class::<PyGlyphPosition>()?;
    m.add_class::<PyGlyphBuffer>()?;
    Ok(())
}
